
# File Processor

This script reads multiple `.dat` files from a specified directory, combines their data, removes duplicates, calculates combined salaries, and generates a single `.csv` file.

## Prerequisites

- Install `xlsxwriter` library:
  ```shell
  pip install xlsxwriter
  ```

## How to Run

1. Place your `.dat` files in a directory (e.g., `input_data`).

2. Run the script with the directory path as an argument:
    ```bash
    python3 file_processor.py --input_dir_name input_data
    ```

3. The output file `combined_data.csv` will be generated in the `result` directory.
