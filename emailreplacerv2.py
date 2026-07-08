import csv
import os

OLD_DOMAIN = "test.chris.uk"
NEW_DOMAIN = "result.chris.uk"
INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
REGISTRY_FILE = "email_registry.txt"  # persists every @result.chris.uk email seen across runs


def load_registry():
    """Load the set of every @result.chris.uk email recorded in past runs."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        for email in sorted(registry):
            f.write(email + "\n")


def find_email_field(fieldnames):
    """Find whichever header corresponds to the email column,
    regardless of spacing/case (e.g. 'Email', 'email_address' -> 'email')."""
    for name in fieldnames:
        normalized = name.lower().replace(" ", "").replace("_", "")
        if normalized == "email" or normalized == "emailaddress":
            return name
    return None


def convert_domain(email):
    """Replace the domain only if it matches OLD_DOMAIN; otherwise leave untouched."""
    if "@" not in email:
        return email, False
    local, _, domain = email.rpartition("@")
    if domain.strip().lower() == OLD_DOMAIN.lower():
        return f"{local}@{NEW_DOMAIN}", True
    return email, False


def main():
    registry = load_registry()

    with open(INPUT_FILE, newline="") as infile, open(OUTPUT_FILE, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        email_field = find_email_field(reader.fieldnames)
        if email_field is None:
            raise ValueError(
                f"No email column found in {INPUT_FILE}. "
                f"Headers seen: {reader.fieldnames}"
            )

        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        converted = 0
        skipped = 0
        for row in reader:
            old_email = row[email_field].strip()
            new_email, changed = convert_domain(old_email)
            if changed:
                converted += 1
            elif old_email:
                skipped += 1
            row[email_field] = new_email
            writer.writerow(row)

            # Record every @result.chris.uk address we produce (or already see) in the registry
            if new_email.lower().endswith(f"@{NEW_DOMAIN}".lower()):
                registry.add(new_email)

    save_registry(registry)
    print(
        f"Wrote {OUTPUT_FILE}; converted {converted} email(s) from "
        f"@{OLD_DOMAIN} to @{NEW_DOMAIN} ({skipped} left unchanged). "
        f"Registry now has {len(registry)} email(s)."
    )


if __name__ == "__main__":
    main()