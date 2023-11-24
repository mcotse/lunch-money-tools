import requests
import logging
import json
import configparser

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

# Function to load original metadata from a JSON file
def load_original_metadata_from_file(filename='data/original_metadata.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("JSON file with original metadata not found.")
        return {}

def rollback_transactions():
    # Load original metadata from the JSON file
    original_metadata = load_original_metadata_from_file()

    # Check if original metadata is loaded
    if not original_metadata:
        logging.error("Rollback aborted: No original metadata available.")
        return

    # Rollback transactions to their original state
    for tx_id, original_data in original_metadata.items():
        if update_transaction(tx_id, original_data):
            logging.info(f"Transaction {tx_id} reverted to original state successfully.")
        else:
            logging.error(f"Failed to revert transaction {tx_id}")

if __name__ == "__main__":
    rollback_transactions()
