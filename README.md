# Ethereum Transaction Importer for Beancount

A [Beancount](https://beancount.github.io/) importer for Ethereum blockchain transactions. Downloads transaction data from [Etherscan](https://etherscan.io/) or compatible block explorers (like [Blockscout](https://blockscout.com/)) and imports them into your Beancount ledger.

## Features

- Downloads normal transactions, internal transactions, and ERC-20 token transfers
- Supports multiple wallet addresses
- Automatic transaction fee tracking
- Currency mapping for stablecoins and wrapped tokens
- Deduplication against existing ledger entries
- Compatible with Etherscan API and Blockscout API

## Requirements

- Python >= 3.9
- Beancount 3.x
- Beangulp 0.2.0+

## Installation

### From PyPI

```bash
pip install beancount-ethereum
```

### From Source

```bash
git clone https://github.com/xuhcc/beancount-ethereum-importer.git
cd beancount-ethereum-importer
pip install -e .
```

### Running Locally Without pip Install

If you prefer to run directly from the repository:

1. Install only the dependencies:

```bash
pip install beancount beangulp
```

2. Clone and enter the repository:

```bash
git clone https://github.com/xuhcc/beancount-ethereum-importer.git
cd beancount-ethereum-importer
```

3. Create your config file:

```bash
cp config.json.example config.json
# Edit config.json with your settings
```

4. Download transactions:

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

5. Run the importer with PYTHONPATH:

```bash
# Identify files
PYTHONPATH=. python import_config.py identify downloads/

# Extract transactions
PYTHONPATH=. python import_config.py extract downloads/

# Extract with deduplication
PYTHONPATH=. python import_config.py extract -e ledger.beancount downloads/
```

## Configuration

Create a `config.json` file based on the example:

```json
{
    "name": "mainnet",
    "default_account": "Assets:Crypto:ETH",
    "account_map": {
        "0xYourWalletAddress1": "Assets:Ethereum:Wallet1",
        "0xYourWalletAddress2": "Assets:Ethereum:Wallet2"
    },
    "fee_account": "Expenses:Crypto:Fees",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY",
    "block_explorer_api_request_delay": 0.2,
    "base_currency": "ETH",
    "currency_map": {
        "USDC": {"commodity": "USD", "account_suffix": "USDC"},
        "WETH": {"commodity": "ETH"}
    }
}
```

### Configuration Options

| Option | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Name for the output file (e.g., `mainnet` creates `mainnet.json`) |
| `default_account` | No | Default account for beangulp (default: `Assets:Crypto:ETH`) |
| `account_map` | Yes | Map of wallet addresses to Beancount account names |
| `fee_account` | Yes | Account for transaction fees |
| `expenses_account` | Yes | Account for outgoing transactions to unknown addresses |
| `income_account` | Yes | Account for incoming transactions from unknown addresses |
| `block_explorer_api_url` | Yes | API endpoint URL |
| `block_explorer_api_key` | No | API key (required for Etherscan) |
| `block_explorer_api_request_delay` | No | Delay between API requests in seconds (default: 0) |
| `base_currency` | No | Base currency symbol (default: `ETH`) |
| `currency_map` | No | Map token symbols to commodities and account suffixes |

### Getting an API Key

- **Etherscan**: Register at https://etherscan.io/register and create an API key
- **Blockscout**: Usually no API key required

### Supported Block Explorers

- Etherscan (Ethereum Mainnet): `https://api.etherscan.io/api`
- Arbiscan (Arbitrum): `https://api.arbiscan.io/api`
- Polygonscan (Polygon): `https://api.polygonscan.com/api`
- Blockscout (various chains): Check their documentation for API URLs

## Usage

### Step 1: Download Transactions

Download transactions from the blockchain:

```bash
beancount-ethereum --config=config.json --output-dir=downloads
```

Or without installation:

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

This creates a JSON file (e.g., `downloads/mainnet.json`) with all transactions.

### Step 2: Create Import Configuration

Create an `import_config.py` file:

```python
#!/usr/bin/env python3
import beangulp
import beancount_ethereum

importers = [
    beancount_ethereum.Importer(config_path='config.json'),
]

if __name__ == '__main__':
    ingest = beangulp.Ingest(importers)
    ingest()
```

### Step 3: Identify Files

Verify the importer recognizes your downloaded files:

```bash
python import_config.py identify downloads/
```

### Step 4: Extract Transactions

Import transactions to Beancount format:

```bash
# Output to stdout
python import_config.py extract downloads/

# Save to file
python import_config.py extract downloads/ > new_transactions.beancount

# Deduplicate against existing ledger
python import_config.py extract -e ledger.beancount downloads/ > new_transactions.beancount
```

### Importer Options

The `Importer` class accepts these parameters:

```python
beancount_ethereum.Importer(
    config_path='config.json',  # Path to configuration file
    max_delta=90,               # Only import transactions from last N days
)
```

## Example Output

The importer generates Beancount transactions like:

```beancount
2024-01-15 * "0x1234...5678"
  txid: "0xabc123..."
  Assets:Ethereum:Wallet1:ETH  -1.5 ETH
  Expenses:Crypto:Other         1.5 ETH
  Assets:Ethereum:Wallet1:ETH  -0.001 ETH
  Expenses:Crypto:Fees          0.001 ETH
```

For transfers between known addresses:

```beancount
2024-01-15 *
  txid: "0xdef456..."
  Assets:Ethereum:Wallet1:ETH  -2.0 ETH
  Assets:Ethereum:Wallet2:ETH   2.0 ETH
  Assets:Ethereum:Wallet1:ETH  -0.0015 ETH
  Expenses:Crypto:Fees          0.0015 ETH
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
PYTHONPATH=. pytest tests/ -v

# Run tests with coverage
PYTHONPATH=. pytest tests/ --cov=beancount_ethereum --cov-report=term-missing
```

## Development

### Project Structure

```
beancount-ethereum-importer/
├── beancount_ethereum/
│   ├── __init__.py       # Package exports
│   ├── __main__.py       # CLI entry point
│   ├── downloader.py     # Etherscan API client
│   └── importer.py       # Beangulp importer
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_downloader.py
│   └── test_importer.py
├── config.json.example
├── import_config.py.example
├── requirements.txt
├── requirements-dev.txt
└── setup.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## Troubleshooting

### "No transactions found"

- Verify your wallet address is correct
- Check if the API key is valid
- Ensure the block explorer URL is correct for your chain

### Rate Limiting

If you get rate limit errors, increase `block_explorer_api_request_delay`:

```json
{
    "block_explorer_api_request_delay": 0.5
}
```

### Missing Token Transfers

Some tokens may not appear if:
- They use non-standard transfer events
- The block explorer doesn't index them

### Old Transactions Not Appearing

By default, only transactions from the last 90 days are imported. Adjust `max_delta`:

```python
beancount_ethereum.Importer(config_path='config.json', max_delta=365)
```

## Deploy

Deploy `beancount-ethereum` to PyPI:

```bash
make deploy
```

## License

GPL-3.0

## Credits

- Original author: [xuhcc](https://github.com/xuhcc)
- Beancount: [Martin Blais](https://github.com/blais)
- Beangulp: [Beancount contributors](https://github.com/beancount/beangulp)
