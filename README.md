# Boat Dealer Scraper

The Boat Dealer Scraper is a Python script that scrapes dealer information from the [Discover Boating website](https://www.discoverboating.com/dealers) and stores the data in a SQLite database and/or exports it to a CSV file.

## Features

- Scrapes dealer name, address, phone number, and website from the Discover Boating website
- Validates phone numbers and website URLs before storing the data
- Supports dry run mode to preview the scraped data without saving to the database
- Exports the scraped data to a CSV file
- Uses a Makefile to simplify common tasks, such as installing dependencies, running the script, and exporting to CSV

## Prerequisites

- Python 3.7 or higher
- The following Python packages:
  - `asyncio`
  - `csv`
  - `sqlite3`
  - `time`
  - `urllib`
  - `phonenumbers`
  - `pyppeteer`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/boat-dealer-scraper.git
```


2. Change to the project directory:
```bash
cd boat-dealer-scraper
```

3. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install the required dependencies:
```bash
make install
```

## Usage

### Running the Scraper

To run the scraper and save the data to the SQLite database, use the following command:
```bash
make run
```

This will create the `dealers.db` SQLite database file and populate the `dealers` table with the scraped data.

### Dry Run

To perform a dry run and preview the scraped data without saving it to the database, use the following command:

```bash
make dryrun
```

This will print the scraped dealer information to the console without modifying the database.

### Exporting to CSV

To export the scraped data from the SQLite database to a CSV file, use the following command:

```bash
make csv
```

This will create the `dealers.csv` file in the project directory.

## Makefile Targets

The project includes a `Makefile` that provides the following targets:

- `install-requirements`: Installs the required Python packages.
- `run`: Runs the scraper and saves the data to the SQLite database.
- `dryrun`: Performs a dry run of the scraper and prints the data to the console.
- `csv`: Exports the scraped data from the SQLite database to a CSV file.
- `format`: Formats the Python code using `black` and `isort`.

## Contributing

If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).


