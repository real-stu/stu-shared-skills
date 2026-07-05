#!/usr/bin/env python3
"""
clean_emails.py — Offline email-list cleaner for higher deliverability.

Reads a CSV or Excel file, finds the email column, and for each row:
  1. Normalizes the address (trims whitespace, lowercases, strips mailto:/<>/quotes).
  2. Auto-fixes straightforward problems (domain typos, bad TLDs, stray dots/punctuation).
  3. Validates the result.
  4. Flags duplicates, role-based addresses, and disposable domains.

It KEEPS every row. Nothing is deleted. The original email column is left intact
so changes can be audited. Three columns are inserted right after the email column:

  email_cleaned  -> the corrected, send-ready address (or "" if missing/unfixable)
  email_status   -> Valid | Fixed | Review | Invalid | Missing
  email_issues   -> semicolon-separated plain-English notes

Output is written in the SAME format as the input (CSV->CSV, xlsx->xlsx).

Usage:
  python clean_emails.py INPUT [-o OUTPUT] [--email-column NAME]

If --email-column is omitted the script auto-detects it. If -o is omitted the
output is written next to the input as "<name>_cleaned.<ext>".

The script prints a summary to stdout. Relay that summary to the user — it is the
"report" that explains what changed and what still needs a human's attention.
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

import pandas as pd


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

# Full-domain typo map. Keys are common misspellings of popular mail providers;
# values are the correct domain. This is the single biggest deliverability win,
# because a typo'd provider domain is an instant hard bounce. Includes .co / .cm
# variants here (rather than as a blanket TLD rule) because .co and .cm are valid
# TLDs for other domains and must not be "fixed" globally.
DOMAIN_TYPOS = {
    # gmail
    "gmial.com": "gmail.com", "gmai.com": "gmail.com", "gmail.co": "gmail.com",
    "gmail.cm": "gmail.com", "gmali.com": "gmail.com", "gmaill.com": "gmail.com",
    "gmail.comm": "gmail.com", "gnail.com": "gmail.com", "gamil.com": "gmail.com",
    "gmal.com": "gmail.com", "gmail.con": "gmail.com", "gmail.cmo": "gmail.com",
    "gmail.ocm": "gmail.com", "gmail.vom": "gmail.com", "gmaul.com": "gmail.com",
    "gmail.om": "gmail.com", "gmail.cim": "gmail.com", "gmail.coml": "gmail.com",
    "gmailcom": "gmail.com", "g-mail.com": "gmail.com", "googlemail.con": "googlemail.com",
    # yahoo
    "yaho.com": "yahoo.com", "yahooo.com": "yahoo.com", "yahoo.co": "yahoo.com",
    "yhaoo.com": "yahoo.com", "yahoo.con": "yahoo.com", "yahoo.cm": "yahoo.com",
    "yahho.com": "yahoo.com", "yahoo.comm": "yahoo.com", "ymail.co": "ymail.com",
    "yahoo.om": "yahoo.com",
    # hotmail
    "hotmial.com": "hotmail.com", "hotmai.com": "hotmail.com", "hotmail.co": "hotmail.com",
    "hotnail.com": "hotmail.com", "hormail.com": "hotmail.com", "hotmail.con": "hotmail.com",
    "hotmail.cm": "hotmail.com", "hotmaill.com": "hotmail.com", "hotmal.com": "hotmail.com",
    "hotmil.com": "hotmail.com",
    # outlook
    "outlok.com": "outlook.com", "outloo.com": "outlook.com", "outlook.co": "outlook.com",
    "outook.com": "outlook.com", "outlook.con": "outlook.com", "outlook.cm": "outlook.com",
    "outloo.com": "outlook.com", "oulook.com": "outlook.com",
    # icloud
    "iclould.com": "icloud.com", "icloud.co": "icloud.com", "iclod.com": "icloud.com",
    "icloud.con": "icloud.com", "icould.com": "icloud.com",
    # aol / live / msn / comcast
    "aol.co": "aol.com", "aol.con": "aol.com", "aol.cm": "aol.com",
    "live.co": "live.com", "live.con": "live.com",
    "msn.co": "msn.com", "msn.con": "msn.com",
    "comcast.net.com": "comcast.net", "comcast.com": "comcast.net",
    "protonmail.co": "protonmail.com", "proton.me.com": "proton.me",
}

# Universally invalid TLDs -> the obviously intended one. Applied to ANY domain,
# because these strings are not real TLDs, so the fix is safe. Deliberately does
# NOT include ".co" or ".cm" (both real TLDs).
BAD_TLDS = {
    "con": "com", "cmo": "com", "ocm": "com", "vom": "com", "xom": "com",
    "comm": "com", "cpm": "com", "ckm": "com", "clm": "com", "coom": "com",
    "cojm": "com", "co.": "com", "nett": "net", "ne": "net", "orgg": "org",
    "edu.": "edu",
}

# Role-based local-parts. These deliver fine but tend to route to shared inboxes,
# get lower engagement, and draw more spam complaints. Kept by default — noted only.
ROLE_LOCALPARTS = {
    "info", "contact", "hello", "support", "admin", "sales", "team", "press",
    "booking", "bookings", "management", "mgmt", "office", "mail", "marketing",
    "pr", "hi", "hey", "help", "inquiries", "enquiries", "partnerships",
    "collabs", "collab", "media", "business", "biz", "agency", "noreply",
    "no-reply", "donotreply",
}

# Common disposable / throwaway domains. Effectively dead for outreach.
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
    "temp-mail.org", "yopmail.com", "throwawaymail.com", "trashmail.com",
    "getnada.com", "maildrop.cc", "dispostable.com", "fakeinbox.com",
    "sharklasers.com", "guerrillamailblock.com", "mailnesia.com", "mintemail.com",
    "spam4.me", "grr.la", "tempinbox.com", "emailondeck.com", "mohmal.com",
    "fakemailgenerator.com", "tempmailo.com", "burnermail.io", "33mail.com",
    "mail-temp.com", "tmpmail.org", "moakt.com", "luxusmail.org",
}

# Practical RFC-5322-lite validation. Not exhaustive, but rejects the formats
# that actually bounce in real lists. Local part: letters/digits and . _ % + -
# (no leading/trailing dot, no consecutive dots). Domain: labels of
# letters/digits/hyphens separated by dots, TLD >= 2 letters.
EMAIL_RE = re.compile(
    r"^(?!\.)(?!.*\.\.)[A-Za-z0-9._%+\-]+(?<!\.)@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}$"
)


# ---------------------------------------------------------------------------
# Cleaning logic
# ---------------------------------------------------------------------------

def normalize(raw: str):
    """Lightweight, lossless-ish normalization. Returns (value, notes)."""
    notes = []
    s = raw.strip()

    # Pull an address out of "Name <addr>" display form.
    m = re.search(r"<([^>]+)>", s)
    if m:
        s = m.group(1).strip()
        notes.append("extracted address from display name")

    before = s
    s = re.sub(r"^\s*mailto:\s*", "", s, flags=re.IGNORECASE)
    if s != before:
        notes.append("removed mailto: prefix")

    s = s.strip().strip('"').strip("'").strip()
    s = re.sub(r"\s+", "", s)            # emails never contain spaces in these lists
    s = s.rstrip(".,;:")                 # trailing punctuation from copy/paste

    lowered = s.lower()
    if lowered != s:
        notes.append("normalized to lowercase")
    s = lowered
    return s, notes


def fix_domain(domain: str):
    """Apply typo corrections to the domain. Returns (domain, notes)."""
    notes = []
    domain = re.sub(r"\.{2,}", ".", domain).strip(".")

    if domain in DOMAIN_TYPOS:
        fixed = DOMAIN_TYPOS[domain]
        notes.append(f"fixed domain typo: {domain} -> {fixed}")
        return fixed, notes

    # TLD-level repair for clearly-invalid TLDs.
    parts = domain.rsplit(".", 1)
    if len(parts) == 2:
        head, tld = parts
        if tld in BAD_TLDS:
            fixed = f"{head}.{BAD_TLDS[tld]}"
            notes.append(f"fixed TLD typo: .{tld} -> .{BAD_TLDS[tld]}")
            # the corrected full domain might itself be a known typo (rare); re-check
            if fixed in DOMAIN_TYPOS:
                fixed2 = DOMAIN_TYPOS[fixed]
                notes.append(f"fixed domain typo: {fixed} -> {fixed2}")
                fixed = fixed2
            return fixed, notes
    return domain, notes


def dedupe_key(email: str) -> str:
    """Canonical key for duplicate detection.

    Gmail/Googlemail ignore dots in the local part and treat everything after
    '+' as a tag, so john.doe+promo@gmail.com and johndoe@gmail.com are the SAME
    inbox. We collapse those for MATCHING only — the stored cleaned address is
    never altered this way.
    """
    if "@" not in email:
        return email
    local, domain = email.rsplit("@", 1)
    local = local.split("+", 1)[0]
    if domain in ("gmail.com", "googlemail.com"):
        local = local.replace(".", "")
        domain = "gmail.com"
    return f"{local}@{domain}"


def clean_one(raw):
    """Clean a single raw cell. Returns (cleaned, status, issues_list)."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)) or str(raw).strip() == "":
        return "", "Missing", ["missing email"]

    issues = []
    s, n = normalize(str(raw))
    issues += n

    if s.count("@") != 1:
        return "", "Invalid", issues + ["invalid format: address must contain exactly one @"]

    local, domain = s.split("@")
    new_local = re.sub(r"\.{2,}", ".", local).strip(".")
    if new_local != local:
        issues.append("fixed stray dots in the address")
        local = new_local
    domain, dn = fix_domain(domain)
    issues += dn
    candidate = f"{local}@{domain}"

    fixed_changed = any(
        msg.startswith(("fixed", "removed mailto", "extracted", "normalized"))
        for msg in issues
    )

    if not EMAIL_RE.match(candidate):
        return "", "Invalid", issues + ["invalid format: failed validation after fixes"]

    # Address is structurally valid. Layer on advisory flags.
    if domain in DISPOSABLE_DOMAINS:
        issues.append("disposable/temporary domain (likely undeliverable)")
        status = "Review"
    elif fixed_changed:
        status = "Fixed"
    else:
        status = "Valid"

    if local in ROLE_LOCALPARTS or local.split("-")[0] in {"no", "do"} and "reply" in local:
        issues.append("role-based address (kept; tends toward lower engagement)")

    return candidate, status, issues


def find_email_column(df, override=None):
    if override:
        if override not in df.columns:
            sys.exit(f"ERROR: column '{override}' not found. Columns: {list(df.columns)}")
        return override
    # exact, then fuzzy
    for c in df.columns:
        if str(c).strip().lower() in ("email", "e-mail", "email address", "emailaddress"):
            return c
    for c in df.columns:
        if "email" in str(c).lower() or "e-mail" in str(c).lower():
            return c
    for c in df.columns:
        if "mail" in str(c).lower():
            return c
    sys.exit(
        "ERROR: could not auto-detect an email column. "
        f"Columns are: {list(df.columns)}. Re-run with --email-column NAME."
    )


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def read_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv", ".txt"):
        sep = "\t" if ext == ".tsv" else None
        # dtype=str keeps phone numbers / IDs / zip codes from being mangled
        return pd.read_csv(path, dtype=str, keep_default_na=False, sep=sep,
                           engine="python"), ext
    if ext in (".xlsx", ".xlsm", ".xls"):
        return pd.read_excel(path, dtype=str, keep_default_na=False), ext
    sys.exit(f"ERROR: unsupported file type '{ext}'. Use .csv, .tsv, .xlsx, .xlsm, or .xls.")


def write_table(df, path, ext):
    if ext in (".csv", ".tsv", ".txt"):
        sep = "\t" if ext == ".tsv" else ","
        df.to_csv(path, index=False, sep=sep)
    else:
        out = path if path.lower().endswith((".xlsx", ".xlsm")) else path + ".xlsx"
        df.to_excel(out, index=False, engine="openpyxl")
        return out
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Clean an email list for deliverability.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--email-column", default=None,
                    help="Name of the email column (auto-detected if omitted).")
    args = ap.parse_args()

    df, ext = read_table(args.input)
    if df.empty:
        sys.exit("ERROR: the file has no rows.")

    email_col = find_email_column(df, args.email_column)

    cleaned, statuses, issues_col = [], [], []
    seen = {}            # dedupe_key -> first row number (1-based, data rows)
    for i, raw in enumerate(df[email_col].tolist()):
        c, status, issues = clean_one(raw)
        if c:
            key = dedupe_key(c)
            if key in seen:
                issues.append(f"duplicate of row {seen[key]} (first occurrence kept)")
                status = "Review"
            else:
                seen[key] = i + 1
        cleaned.append(c)
        statuses.append(status)
        issues_col.append("; ".join(issues))

    # Insert the three new columns immediately after the email column.
    insert_at = df.columns.get_loc(email_col) + 1
    for name, values in (("email_cleaned", cleaned),
                         ("email_status", statuses),
                         ("email_issues", issues_col)):
        if name in df.columns:                 # avoid clobber on re-runs
            name = name + "_2"
        df.insert(insert_at, name, values)
        insert_at += 1

    out_path = args.output
    if not out_path:
        root, _ = os.path.splitext(args.input)
        out_path = f"{root}_cleaned{ext if ext in ('.csv', '.tsv', '.txt') else '.xlsx'}"
    final_path = write_table(df, out_path, ext)

    # ---- Summary -----------------------------------------------------------
    total = len(df)
    counts = Counter(statuses)
    fixed_examples = []
    flag_counts = defaultdict(int)
    for raw, c, st, iss in zip(df[email_col], cleaned, statuses, issues_col):
        if "fixed domain typo" in iss or "fixed TLD typo" in iss:
            if len(fixed_examples) < 8:
                fixed_examples.append(f"    {str(raw).strip()} -> {c}")
        if "role-based" in iss:
            flag_counts["role-based"] += 1
        if "disposable" in iss:
            flag_counts["disposable"] += 1
        if "duplicate of row" in iss:
            flag_counts["duplicate"] += 1

    print("=" * 60)
    print("EMAIL DELIVERABILITY CLEANING SUMMARY")
    print("=" * 60)
    print(f"Input              : {args.input}")
    print(f"Email column       : {email_col}")
    print(f"Rows processed     : {total}")
    print("-" * 60)
    print("Status breakdown:")
    for st in ("Valid", "Fixed", "Review", "Invalid", "Missing"):
        if counts.get(st):
            print(f"  {st:<8}: {counts[st]:>5}")
    print("-" * 60)
    print("Flags (rows kept, surfaced in email_issues):")
    print(f"  role-based addresses : {flag_counts['role-based']}")
    print(f"  disposable domains   : {flag_counts['disposable']}")
    print(f"  duplicate inboxes    : {flag_counts['duplicate']}")
    if fixed_examples:
        print("-" * 60)
        print("Sample auto-fixes:")
        print("\n".join(fixed_examples))
    print("-" * 60)
    sendable = counts.get("Valid", 0) + counts.get("Fixed", 0)
    print(f"Send-ready (Valid + Fixed): {sendable} of {total}")
    print(f"Output written     : {final_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
