import csv
import re

from checksum import calculate_checksum, serialize_result


CSV_FILE = "1.csv"
VARIANT = 1

reg_patterns = {
    "email"              : r"^[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}$",
    "http_status_message": r"^\d{3}\s[A-Za-z][A-Za-z\s]*$",
    "snils"              : r"^\d{11}$",
    "passport"           : r"^\d{2}\s\d{2}\s\d{6}$",
    "ip_v4"              : r"^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$",
    "longitude"          : r"^-?(?:180(?:\.0{1,6})?|(?:1[0-7]\d|[1-9]?\d)(?:\.\d{1,6})?)$",
    "hex_color"          : r"^#[0-9a-fA-F]{6}$",
    "isbn"               : r"^\d{3}-\d-\d{5}-\d{3}-\d$",
    "locale_code"        : r"^[a-z]{2}(?:-[a-z]{2})?$",
    "time"               : r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d{1,6})$",
}


def is_row_valid(row):
    for column, pattern in reg_patterns.items():
        if not re.fullmatch(pattern, row[column]):
            return False

    return True


def get_invalid_rows(filename):
    invalid_rows_numbers = []

    with open(filename, mode="r", encoding="utf-16", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row_number, row in enumerate(reader):
            if not is_row_valid(row):
                invalid_rows_numbers.append(row_number)

    return invalid_rows_numbers


def main():
    invalid_rows = get_invalid_rows(CSV_FILE)
    checksum = calculate_checksum(invalid_rows)

    serialize_result(VARIANT, checksum)

    print("Invalid rows:", len(invalid_rows))
    print("Checksum:", checksum)


if __name__ == "__main__":
    main()