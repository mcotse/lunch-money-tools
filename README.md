
# Lunch Money Transaction Tools

## Overview
This script automates the process of updating transaction metadata in the Lunch Money app. It identifies refund transactions and pairs them with corresponding charges. When a match is found, it updates the payee name and date to reflect that the transaction was refunded.

## Features
- Fetch transactions within a user-defined date range.
- Identify and match charge and refund transactions.
- Update transaction metadata to mark refunds.
- Save original transaction data for potential rollback.
- Preview changes before applying updates.

## Requirements
- Python 3
- `requests` library
- A valid Lunch Money API key

## Setup
1. **Clone the Repository:**
   ```
   git clone https://github.com/mcotse/lunch-money-tools.git
   ```
2. **Navigate to the Script Directory:**
   ```
   cd lunch-money-tools
   ```
3. **Install Dependencies:**
   Ensure you have the `requests` library installed. If not, install it using pip:
   ```
   pip install requests
   ```

## Configuration
1. **API Key:**
   - Place your Lunch Money API key in a `.config` file in the following format:
     ```
     [DEFAULT]
     LUNCHMONEY_API_KEY = Your_API_Token
     ```
   - Ensure the `.config` file is in the same directory as the script.

## Usage
1. **Run the Script:**
   ```
   python tx_script.py
   ```
2. **Enter the Date Range:**
   - You will be prompted to enter the start and end dates for the transaction period you want to process.
   - The end date is optional and defaults to today's date if not provided.

3. **Preview and Confirm Updates:**
   - The script will display the planned transaction updates.
   - Confirm to proceed with the updates or abort the process.

4. **Rollback (if necessary):**
   - If you need to revert the changes, use the `rollback.py` script.
   - This script will use the saved original data to restore the transactions.

## Contributing
Feel free to fork the repository and submit pull requests.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact
- GitHub: [@mcotse](https://github.com/mcotse)
