---
name: email-deliverability-cleaner
description: >-
  Clean and validate a list of email addresses in a CSV or Excel file to improve
  deliverability before sending outreach, newsletters, or campaigns. Use this
  whenever someone hands over a spreadsheet or CSV of contacts/leads/members/
  subscribers/creators and wants the emails scrubbed, validated, de-duplicated,
  bounce-proofed, or "cleaned up" — including requests like "fix the emails in
  this list", "clean my mailing list", "check these emails before I send", "scrub
  this contact export", "remove bad emails", "dedupe these subscribers", "why are
  my emails bouncing", or "prep this list for Mailchimp/Klaviyo/a blast". Trigger
  it even when the person doesn't say the word "deliverability" — any task whose
  goal is a healthier, more sendable email column belongs here. Do NOT use it for
  composing or sending email, or for spreadsheet work unrelated to email columns.
---

# Email Deliverability Cleaner

## What this does and why it matters

Sending to bad addresses is the fastest way to wreck a sender reputation: hard
bounces, spam-trap hits, and low engagement all tell inbox providers to start
routing your mail to spam. This skill scrubs the email column of a CSV or Excel
file so the list is healthier before anything goes out.

It is **non-destructive**. Every row is kept. The original email column is left
untouched so changes are auditable, and three new columns are inserted right
after it:

| Column | Meaning |
|---|---|
| `email_cleaned` | The corrected, send-ready address (blank if missing or unfixable) |
| `email_status` | `Valid`, `Fixed`, `Review`, `Invalid`, or `Missing` |
| `email_issues` | Plain-English notes on what was fixed or flagged |

The output is written in the **same format as the input** (CSV→CSV, Excel→Excel).

### What "status" means

- **Valid** — clean and structurally sound; send away.
- **Fixed** — had a fixable problem (a domain typo, stray whitespace, a `mailto:`
  prefix, etc.) that was auto-corrected. Now send-ready.
- **Review** — deliverable in form but risky: a disposable/throwaway domain, or a
  duplicate of an inbox already in the list. Kept, but worth a human glance.
- **Invalid** — structurally broken and not safely auto-fixable (e.g. junk
  characters, two `@` signs). `email_cleaned` is blank. Don't send.
- **Missing** — the row had no email at all.

`Valid + Fixed` is the count that's truly ready to send.

## What gets auto-fixed vs. only flagged

**Auto-fixed** (the address is rewritten in `email_cleaned`):
- Leading/trailing whitespace, and stray spaces inside the address
- Uppercase normalized to lowercase
- `mailto:` prefixes and `Name <addr>` display-name wrappers stripped
- Surrounding quotes and trailing punctuation removed
- Provider domain typos: `gmial.com`, `yahooo.com`, `hotnail.com`, `gmail.co`,
  `outlok.com`, etc. → the correct domain
- Clearly-invalid TLDs: `.con`, `.cmo`, `.comm`, `.ocm` → `.com` (and similar)
- Doubled/leading/trailing dots collapsed

**Flagged but kept** (noted in `email_issues`, status unchanged or set to Review):
- **Role-based addresses** (`info@`, `contact@`, `hello@`, `sales@`, …) — kept by
  default because they're often a real business inbox, but flagged because they
  trend toward lower engagement and more spam complaints.
- **Disposable domains** (`mailinator.com`, `10minutemail.com`, …) — almost
  always dead for outreach → `Review`.
- **Duplicates** — the second and later appearances of the same inbox are flagged
  (`duplicate of row N`), with gmail's dot/`+tag` rules accounted for, so
  `john.doe+x@gmail.com` and `johndoe@gmail.com` are recognized as one inbox.

## Workflow

1. **Find the file.** Uploaded files live in `/mnt/user-data/uploads/`. If the
   path isn't already known, list that directory.

2. **Run the cleaner.** It handles `.csv`, `.tsv`, `.xlsx`, `.xlsm`, and `.xls`,
   auto-detects the email column, and writes the cleaned file to
   `/mnt/user-data/outputs/`:

   ```bash
   python /path/to/skills/email-deliverability-cleaner/scripts/clean_emails.py \
     "/mnt/user-data/uploads/INPUT.csv" \
     -o "/mnt/user-data/outputs/INPUT_cleaned.csv"
   ```

   - If the email column isn't auto-detected (or there are several email-like
     columns and you need a specific one), pass `--email-column "NAME"`.
   - The output extension should match the input. For Excel inputs, keep the
     `.xlsx` extension on the output path.

3. **Relay the summary.** The script prints a summary block (rows processed,
   status breakdown, flag counts, sample auto-fixes, and the send-ready total).
   Report those numbers to the person in your own words — this is the "what
   changed" explanation they need. Call out anything that needs their attention:
   Invalid rows to look at, the number of duplicates they may want to drop, and
   any disposable domains.

4. **Hand back the file** with `present_files`, pointing at the cleaned output.

## Setting expectations on deliverability (important)

This is **offline** cleaning: syntax, typos, normalization, duplicates, and
role/disposable detection. That catches the large majority of issues that cause
bounces. It does **not** confirm that a mailbox actually exists, because that
requires a live network check (MX-record and SMTP probing) against a verification
service, which isn't available here.

So be honest about scope: a `Valid` status means *well-formed and likely
deliverable*, not *guaranteed to land*. If someone needs certainty (e.g. before a
large paid send), tell them the remaining step is to run the `Valid + Fixed`
addresses through a live verification service (ZeroBounce, NeverBounce, Kickbox,
Bouncer, etc.) to catch dead-but-well-formed mailboxes. Don't imply the offline
pass alone guarantees inbox placement.

## Notes and edge cases

- **Multiple email columns** (e.g. `email` and `secondary_email`): the script
  cleans one column per run. Run it again with `--email-column` for the second.
- **Excel formatting** isn't preserved — the data is rewritten to a fresh sheet.
  The values, columns, and order are kept; cell colors/merged cells are not. If a
  person needs the original styling intact, mention that trade-off.
- **Re-running** on an already-cleaned file won't clobber the prior columns; new
  ones get a `_2` suffix.
- IDs, phone numbers, and zip codes are read as text, so leading zeros and long
  numbers won't be mangled.
