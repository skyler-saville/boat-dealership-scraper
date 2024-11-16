#!/usr/bin/env python3

import argparse
import asyncio
import csv
import os
import sqlite3
import time
from urllib.parse import urlparse  # for website URL validation

from phonenumbers import geocoder, is_valid_number
from phonenumbers import parse as parse_number  # for phone number validation
from pyppeteer import launch

DB_NAME = "dealers.db"
TABLE_NAME = "dealers"


async def setup_database(conn):
    # Check if database file exists
    if not os.path.exists(DB_NAME):
        print(f"Database file '{DB_NAME}' not found. Creating a new one.")
    cursor = conn.cursor()

    # Check if table exists (optional)
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'"
    )
    table_exists = cursor.fetchone() is not None

    # Drop table if not doing dry run or CSV export (optional)
    if table_exists:
        cursor.execute(f"DROP TABLE {TABLE_NAME}")
        print(f"Dropped existing '{TABLE_NAME}' table.")

    # Create table if it doesn't exist
    cursor.execute(
        f"""CREATE TABLE {TABLE_NAME} (
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT,
        website TEXT
    )"""
    )
    print(f"Created '{TABLE_NAME}' table.")

    conn.commit()


async def validate_and_insert_dealer(conn, dealer_info):
    # Validate phone number
    if dealer_info["phone"]:
        try:
            parsed_phone = parse_number(dealer_info["phone"], "US")
            if not is_valid_number(parsed_phone):
                print(f"Invalid phone number: {dealer_info['phone']}")
                return
        except:
            print(f"Invalid phone number: {dealer_info['phone']}")
            return

    # Validate website URL
    if dealer_info["website"]:
        parsed_url = urlparse(dealer_info["website"])
        if not all([parsed_url.scheme, parsed_url.netloc]):
            print(f"Invalid website URL: {dealer_info['website']}")
            return

    # Insert dealer into database
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (name, address, phone, website) VALUES (?, ?, ?, ?)",
        (
            dealer_info["name"],
            dealer_info["address"],
            dealer_info["phone"],
            dealer_info["website"],
        ),
    )
    conn.commit()


async def scrape_dealers(
    page_number: int, conn: sqlite3.Connection, browser, print_dealers: bool = False
) -> int:
    page = await browser.newPage()

    # Construct URL with page number
    url = f"https://www.discoverboating.com/dealers?page={page_number}"

    # Navigate to the website
    await page.goto(url)

    # Wait for the dealer elements to load
    await page.waitForSelector(".dealer")

    # Extract dealer information
    dealers = await page.querySelectorAll(".dealer")

    # Counter for dealers on this page
    dealers_count = 0

    for dealer in dealers:
        name_element = await dealer.querySelector("h2")
        name = await page.evaluate("(element) => element.textContent", name_element)

        address_element = await dealer.querySelector(".dealer-address")
        address = await page.evaluate(
            "(element) => element.textContent", address_element
        )

        phone_element = await dealer.querySelector(".dealer-phone")
        phone = (
            await page.evaluate(
                '(element) => element.getAttribute("data-title")', phone_element
            )
            if phone_element
            else None
        )

        website_element = await dealer.querySelector('a[title="Website"]')
        website = (
            await page.evaluate(
                '(element) => element.getAttribute("href")', website_element
            )
            if website_element
            else None
        )

        # Add validated data to insert list
        dealer_info = {
            "name": name.strip(),
            "address": address.strip(),
            "phone": phone.strip() if phone else None,
            "website": website.strip() if website else None,
        }

        # Validate and insert dealer
        await validate_and_insert_dealer(conn, dealer_info)

        # Print dealer information
        if print_dealers:
            print(f"Dealer {dealers_count + 1}: {dealer_info}")

        dealers_count += 1

    await page.close()

    # Return the number of dealers processed
    return dealers_count


async def scrape_all_dealers(conn: sqlite3.Connection, print_dealers: bool = False):
    total_pages = 411  # Update with the actual total number of pages

    print("Scraping dealer information from the website...")

    # Launch browser
    browser = await launch()

    # Iterate over all pages and scrape dealer information
    total_dealers = 0
    for page_number in range(total_pages):
        start_time = time.time()  # starting time
        dealers_count = await scrape_dealers(page_number, conn, browser, print_dealers)
        end_time = time.time()  # Ending time
        total_dealers += dealers_count
        print(
            f"Page {page_number}: Loaded {dealers_count} dealers {end_time - start_time:.2f} seconds."
        )

    print(f"Total dealers scraped: {total_dealers}")

    await browser.close()


async def save_to_csv_from_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_NAME)

    # Select all dealers from the database
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_NAME}")

    print("Exporting dealer information to CSV...")

    if not os.path.exists("dealers.csv"):
        print("dealers.csv file not found. Creating a new one.")

    # Open CSV file in write mode with newline=''
    with open("dealers.csv", "w", newline="") as csvfile:
        fieldnames = ["name", "address", "phone", "website"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Iterate over dealer rows and write to CSV
        for row in c:
            writer.writerow(
                {"name": row[0], "address": row[1], "phone": row[2], "website": row[3]}
            )

    print("CSV export complete.")
    conn.close()


async def main():
    parser = argparse.ArgumentParser(description="Boat Scraper")
    parser.add_argument("--dryrun", action="store_true", help="Perform a dry run")
    parser.add_argument(
        "--csv", action="store_true", help="Save dealers to CSV file from the database"
    )
    args = parser.parse_args()

    # Connect to database
    conn = sqlite3.connect(DB_NAME)

    if args.dryrun:
        print("Dry run mode enabled. No data will be saved to the database.")
        await scrape_all_dealers(conn, print_dealers=True)  # Pass print_dealers here
    elif args.csv:
        await save_to_csv_from_db()
    else:
        # Drop the tables and start with fresh database
        await setup_database(conn)
        await scrape_all_dealers(conn)

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
