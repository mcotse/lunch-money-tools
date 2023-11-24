""" 
This script automates the process of updating transaction metadata in the Lunch Money app. It performs the following key functions:

1. Retrieves all transactions from the Lunch Money API, fetching them month by month.
2. Constructs two dictionaries:
   - A mapping of transaction amounts to their respective IDs.
   - A mapping of transaction IDs to their detailed metadata.
3. Identifies refund transactions and matches them with their corresponding charge transactions based on the transaction amount.
4. For each matched pair of charge and refund, if the payee is the same, the script prepares new metadata. This metadata includes updating the payee name to indicate a refund and setting the date to the charge transaction's date.
5. Executes PUT requests to the Lunch Money API to update the metadata of these transactions.

The script uses Python's `requests` library for API interactions and `logging` for tracking its operations. API authentication is managed through a token loaded from a `.config` file.

Requirements:
- Python 3
- `requests` library
- A `.config` file containing the API token

Usage:
- Ensure the API token is set in the `.config` file under the key `LUNCHMONEY_API_KEY`.
- Run the script in a Python environment where `requests` is installed.
"""

import requests
import datetime
import logging
import configparser
import json

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load API token from .config file
config = configparser.ConfigParser()
config.read('.config')
TOKEN = config['DEFAULT']['LUNCHMONEY_API_KEY']  # Replace .config with your config file's path if necessary

# Constants
BASE_URL = "https://dev.lunchmoney.app/v1/transactions"
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

# Function to get transactions for a given month
def get_transactions_for_month(start_date, end_date):
    params = {'start_date': start_date, 'end_date': end_date}
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json().get('transactions', [])
    except requests.RequestException as e:
        logging.error(f"Error fetching transactions: {e}")
        return []

# Function to update a transaction
def update_transaction(transaction_id, metadata):
    url = f"{BASE_URL}/{transaction_id}"
    try:
        response = requests.put(url, headers=HEADERS, json={"transaction": metadata})
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logging.error(f"Error updating transaction {transaction_id}: {e}")
        return False
    
# Function to revert a transaction to its original state
def revert_transaction(transaction_id, original_metadata):
    return update_transaction(transaction_id, original_metadata)

# Function to save original metadata to a JSON file
def save_original_metadata_to_file(metadata, start_date, end_date):
    filename=f'data/original_metadata_{start_date}_{end_date}.json'
    with open(filename, 'w') as file:
        json.dump(metadata, file, indent=4)
    logging.info("Original metadata saved to file.")

def gather_transactions(start_date, end_date):
    amount_to_id = {}
    id_to_metadata = {}
    current_end_date = end_date

    while current_end_date > start_date:
        current_start_date = current_end_date - datetime.timedelta(days=30)
        if current_start_date < start_date:
            current_start_date = start_date

        transactions = get_transactions_for_month(current_start_date.isoformat(), current_end_date.isoformat())
        for tx in transactions:
            tx_id = tx['id']
            amount = float(tx['amount'])
            amount_to_id[amount] = tx_id
            id_to_metadata[tx_id] = tx

        current_end_date = current_start_date

    return amount_to_id, id_to_metadata

def process_transactions(amount_to_id, id_to_metadata):
    charge_to_refund = {}
    tx_to_update_metadata = {}
    negative_amount_to_id = {amount: tx_id for amount, tx_id in amount_to_id.items() if float(amount) < 0}
    for amount, tx_id in negative_amount_to_id.items():
        if -amount in amount_to_id:
            charge_to_refund[amount_to_id[-amount]] = tx_id

    for charge_id, refund_id in charge_to_refund.items():
        charge = id_to_metadata[charge_id]
        refund = id_to_metadata[refund_id]
        if (charge['payee'] == refund['payee'] and 
            charge['date'] != refund['date'] and 
            'refunded' not in charge['payee']):
            updated_metadata = {"payee": f"{charge['payee']} (refunded)", "date": charge['date']}
            tx_to_update_metadata[charge_id] = updated_metadata
            tx_to_update_metadata[refund_id] = updated_metadata
    return tx_to_update_metadata

def preview_and_confirm_updates(tx_to_update_metadata, id_to_metadata):
    print("The following transactions will be updated:")
    for tx_id, metadata in tx_to_update_metadata.items():
        original_data = id_to_metadata[tx_id]
        print(f"\nTransaction ID: {tx_id}")
        print(f"Original Payee: {original_data['payee']}, Date: {original_data['date']}")
        print(f"Updated Payee: {metadata['payee']}, Date: {metadata['date']}")

    confirm_update = input("\nDo you want to proceed with these updates? (yes/no): ")
    return confirm_update.lower() == 'yes'

def perform_updates(tx_to_update_metadata, id_to_metadata, start_date, end_date):
    original_metadata = {tx_id: id_to_metadata[tx_id] for tx_id in tx_to_update_metadata}
    save_original_metadata_to_file(original_metadata, start_date, end_date)

    for tx_id, metadata in tx_to_update_metadata.items():
        if update_transaction(tx_id, metadata):
            logging.info(f"Transaction {tx_id} updated successfully.")
        else:
            logging.error(f"Failed to update transaction {tx_id}")
            break  # Optional: Stop updating if any update fails

def get_date_input(prompt, default=None):
    while True:
        date_str = input(prompt)
        if not date_str and default:
            return default
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def validate_date_range(start_date, end_date):
    if start_date > end_date:
        print("Start date cannot be after end date.")
        return False
    return True

def main():
    print("Enter the date range for processing transactions:")
    start_date = get_date_input("Start date (YYYY-MM-DD): ")
    end_date = get_date_input("End date (YYYY-MM-DD), or press Enter for today's date: ", default=datetime.date.today())

    if not validate_date_range(start_date, end_date):
        return

    # Rest of the script remains the same
    amount_to_id, id_to_metadata = gather_transactions(start_date, end_date)
    tx_to_update_metadata = process_transactions(amount_to_id, id_to_metadata)

    if preview_and_confirm_updates(tx_to_update_metadata, id_to_metadata):
        perform_updates(tx_to_update_metadata, id_to_metadata, start_date, end_date)
    else:
        print("Update process aborted.")

if __name__ == "__main__":
    main()



"""
original GPT4-prompt:
What it does:
- get all tx with get a month at a time, loop if more than a month
- make dict of {amount:id} and {id:metadata}
- filter for all the refunds 
- for each refunded item, if the |amount| is in the amount_to_id dict, make dict of {charge:refund}
- make new tx_to_updated_metadata dict
- for each item in charge:refund, if payee is same:
    - set updated_metadata as a dictof {"payee": payee + "(refunded)"}, "date":charge_date}
    - add charge_tx_id:updated_metadata to tx_to_update_metadata
    - add refund_tx_id:updated_metadata to tx_to_update_metadata
- for each item in tx_to_update_metadata:
    - make PUT request to update transaction

"""