import csv
import os
import xlsxwriter
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def read_dat_file(file_path):
    """Read a .dat file and return headers and rows."""
    try:
        with open(file_path, "r") as file:
            reader = csv.reader(file, delimiter="\t")
            headers = next(reader)
            rows = [row for row in reader]
        return headers, rows
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise


def ensure_directory_exists(directory):
    """Ensure the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def combine_deduplicate_and_calculate_salary(all_rows):
    """
    Combine lists of rows from multiple files, remove duplicates, and calculate combined salary.

    This function takes a list of lists of rows (from multiple files), removes duplicate rows, and calculates the combined
    salary (basic salary + allowances) for each unique row. It appends the combined salary to each row and returns a list
    of these unique rows with the combined salary included.
    """
    unique_rows_set = set()
    combined_rows = []

    for rows in all_rows:
        for row in rows:
            row_tuple = tuple(row)
            if row_tuple not in unique_rows_set:
                unique_rows_set.add(row_tuple)
                try:
                    # Calculate combined salary (basic_salary + allowances)
                    # row[5] is basic_salary & row[6] is allowances
                    combined_salary = int(row[5]) + int(row[6])
                    row_with_combined_salary = row + [combined_salary]
                    combined_rows.append(row_with_combined_salary)
                except ValueError as e:
                    logging.error(f"Error converting salary to int in row {row}: {e}")
                    raise
                except IndexError as e:
                    logging.error(f"Error accessing salary data in row {row}: {e}")
                    raise

    logging.info(f"Processed {len(combined_rows)} unique rows.")
    return combined_rows


def calculate_salaries(rows):
    """Calculate second highest and average salaries."""
    try:
        salaries = [int(row[-1]) for row in rows]
        unique_salaries = list(sorted(set(salaries)))
        second_highest_salary = unique_salaries[-2]
        average_salary = round(sum(salaries) / len(salaries), 1)
        return second_highest_salary, average_salary
    except ValueError as e:
        logging.error(f"Error converting salary to int: {e}")
        raise
    except IndexError as e:
        logging.error(f"Error accessing salary data: {e}")
        raise


def write_to_csv(headers, rows, second_highest_salary, average_salary, output_file):
    """Write headers, rows, and salary information to a CSV file."""
    try:
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet()

        # Set column widths
        worksheet.set_column(0, len(headers) - 1, 15)

        # Define cell format
        header_format = workbook.add_format({"align": "left"})
        cell_format = workbook.add_format({"align": "right"})
        footer_format = workbook.add_format({"align": "left"})

        # Write headers
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Write data rows
        for row_num, row in enumerate(rows, start=1):
            for col_num, cell in enumerate(row):
                worksheet.write(row_num, col_num, cell, cell_format)

        # Write footer information
        footer_start_row = len(rows) + 1
        worksheet.write(
            footer_start_row,
            0,
            f"Second Highest Salary={second_highest_salary}",
            footer_format,
        )
        worksheet.merge_range(
            footer_start_row,
            1,
            footer_start_row,
            2,
            f"Average Salary={average_salary}",
            footer_format,
        )

        workbook.close()
        logging.info(f"Data combined and written to {output_file}")
    except Exception as e:
        logging.error(f"Error writing to output file {output_file}: {e}")
        raise


def main(input_dir):
    input_files = []
    for file in os.listdir(input_dir):
        if file.endswith(".dat"):
            input_files.append(os.path.join(input_dir, file))

    if not input_files:
        logging.error(f"No .dat files present in {input_dir} repository")
        raise

    all_headers = []
    all_rows = []

    # Read input files
    for file in input_files:
        headers, rows = read_dat_file(file)
        all_headers.append(headers)
        all_rows.append(rows)

    # Check if all headers match
    if not all(header == all_headers[0] for header in all_headers):
        logging.warning(
            "Headers do not match between files. Using headers from the first file."
        )

    output_dir = "result"
    output_file = os.path.join(output_dir, "combined_data.csv")

    # Ensure the output directory exists
    ensure_directory_exists(output_dir)

    # Combine data and remove duplicates and add gross salary to it
    unique_rows = combine_deduplicate_and_calculate_salary(all_rows)

    # fetch and update header since Gross Salay has been added in above function
    headers1 = all_headers[0]
    headers1.append("Gross Salary")

    # Calculate salaries
    second_highest_salary, average_salary = calculate_salaries(unique_rows)

    # Write to CSV
    write_to_csv(
        headers1, unique_rows, second_highest_salary, average_salary, output_file
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combine .dat files and calculate salary statistics."
    )
    parser.add_argument(
        "--input_dir_name", required=True, help="Input directory name/path"
    )

    args = parser.parse_args()
    main(args.input_dir_name)
