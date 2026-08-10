# Email Domain Converter

A command line tool that converts email addresses in a CSV file from `test.chris.uk` or `testing.chris.uk` to `result.chris.uk`, while making sure every converted address stays unique across all runs.

## What it does

1. Reads a CSV file you provide.
2. Finds the column containing email addresses (works with headers like `Email`, `email`, `email_address`, etc.).
3. For each row, if the email domain is `test.chris.uk` or `testing.chris.uk`, it rewrites the domain to `result.chris.uk`.
4. If the new address has already been used in a previous run, it appends a number to the local part until it is unique (e.g. `jane.doe@result.chris.uk` becomes `jane.doe2@result.chris.uk`).
5. Appends the results to a single master file, `output.csv`.
6. Keeps a running record of every `result.chris.uk` address ever created, in `email_registry.txt`, so duplicates are caught even across separate runs.
7. Rows with invalid emails (missing `@`, empty local part, etc.) are copied through unchanged and flagged as invalid in the summary.

## Files it creates

| File | Purpose |
|---|---|
| `output.csv` | Master file that every processed batch is appended to |
| `email_registry.txt` | List of every `result.chris.uk` email created so far, used to detect duplicates |

## How to run it

```
python convert_emails.py
```

You will be prompted to enter the path to a CSV file. After it finishes, you can choose to process another batch or exit.

```
Enter the CSV file to process: batch1.csv

--- Batch Summary ---
Batch filename:              batch1.csv
Records processed:           100
New email addresses created: 95
Duplicates handled:          5
Output written to:           output.csv
---------------------

Do you want to process another batch? (Y/N):
```

## Notes

- The input CSV must have a header row with an email column.
- Rows with domains other than `test.chris.uk` or `testing.chris.uk` are left untouched.
- Running the script multiple times on the same or different batches is safe. The registry file makes sure no two `result.chris.uk` addresses ever collide.
- If `output.csv` already contains `result.chris.uk` addresses from before the registry file existed, they are automatically picked up and added to the registry the first time you run the script.
