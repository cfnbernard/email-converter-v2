import csv
import os

OLD_DOMAIN = "test.chris.uk"
NEW_DOMAIN = "result.chris.uk"
OUTPUT_FILE = "output.csv"  # all batches are appended to this single master file
REGISTRY_FILE = "email_registry.txt"  # persists every @result.chris.uk email seen across runs


def load_registry():
    """Load the set of every @result.chris.uk email recorded in past runs."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            return set(line.strip().lower() for line in f if line.strip())
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
        if normalized in ("email", "emailaddress"):
            return name
    return None


def is_valid_email(email):
    """Basic validity check: non-empty, exactly one '@', with something on both sides."""
    if not email or email.count("@") != 1:
        return False
    local, domain = email.split("@")
    return bool(local) and bool(domain)


def convert_domain(email):
    """Replace the domain only if it matches OLD_DOMAIN; otherwise leave untouched."""
    local, _, domain = email.rpartition("@")
    if domain.strip().lower() == OLD_DOMAIN.lower():
        return f"{local}@{NEW_DOMAIN}"
    return email


def process_batch(input_file, registry):
    """Process a single CSV batch: convert domains, update the registry, write output.
    Returns a dict of summary stats."""
    write_header = not os.path.exists(OUTPUT_FILE)

    with open(input_file, newline="") as infile, open(OUTPUT_FILE, "a", newline="") as outfile:
        reader = csv.DictReader(infile)
        email_field = find_email_field(reader.fieldnames)
        if email_field is None:
            raise ValueError(
                f"No email column found in {input_file}. "
                f"Headers seen: {reader.fieldnames}"
            )

        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        if write_header:
            writer.writeheader()

        stats = {"processed": 0, "new": 0, "duplicates": 0, "invalid": 0}

        for row in reader:
            stats["processed"] += 1
            email = row[email_field].strip()

            if not is_valid_email(email):
                stats["invalid"] += 1
                writer.writerow(row)
                continue

            new_email = convert_domain(email)
            row[email_field] = new_email
            writer.writerow(row)

            if new_email.lower().endswith(f"@{NEW_DOMAIN}".lower()):
                if new_email.lower() in registry:
                    stats["duplicates"] += 1
                else:
                    registry.add(new_email.lower())
                    stats["new"] += 1

    stats["output_file"] = OUTPUT_FILE
    return stats


def print_summary(input_file, stats):
    print("\n--- Batch Summary ---")
    print(f"Batch filename:              {input_file}")
    print(f"Records processed:           {stats['processed']}")
    print(f"New email addresses created: {stats['new']}")
    print(f"Duplicates handled:          {stats['duplicates']}")
    if stats["invalid"]:
        print(f"Invalid records skipped:     {stats['invalid']}")
    print(f"Output written to:           {stats['output_file']}")
    print("---------------------\n")


def main():
    registry = load_registry()

    while True:
        input_file = input("Enter the CSV file to process: ").strip()

        if not os.path.exists(input_file):
            print(f"File not found: {input_file}\n")
            continue

        stats = process_batch(input_file, registry)
        save_registry(registry)
        print_summary(input_file, stats)

        again = input("Do you want to process another batch? (Y/N): ").strip().lower()
        if again != "y":
            print("Exiting.")
            break


if __name__ == "__main__":
    main()