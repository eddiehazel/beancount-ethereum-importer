# Ethereum Transaction Importer for Beancount

Import your Ethereum blockchain transactions into [Beancount](https://beancount.github.io/), a powerful plain-text accounting system. This tool downloads your transaction history from Etherscan and converts it into Beancount format for tracking your crypto portfolio.

## What This Tool Does

1. **Downloads** your Ethereum transaction history from Etherscan (or similar block explorers)
2. **Converts** those transactions into Beancount's plain-text accounting format
3. **Tracks** ETH transfers, gas fees, and ERC-20 token movements automatically

---

## Complete Beginner's Guide: Zero to Hero

This guide assumes you're starting from scratch. We'll set up everything step by step.

### Prerequisites

You need:
- **Python 3.9+** installed on your computer
- **An Ethereum wallet address** you want to track
- **An Etherscan API key** (free to create)

### Step 1: Install Python Dependencies

Open your terminal and install the required packages:

```bash
pip install beancount beangulp
```

### Step 2: Get the Code

Clone this repository:

```bash
git clone https://github.com/xuhcc/beancount-ethereum-importer.git
cd beancount-ethereum-importer
```

Your folder now looks like this:
```
beancount-ethereum-importer/
├── beancount_ethereum/      # The importer code
├── config.json.example      # Example configuration
├── import_config.py.example # Example import script
└── ...
```

### Step 3: Get Your Etherscan API Key

1. Go to [https://etherscan.io/register](https://etherscan.io/register)
2. Create a free account
3. Go to [https://etherscan.io/myapikey](https://etherscan.io/myapikey)
4. Click "Add" to create a new API key
5. Copy the API key (looks like: `ABCD1234EFGH5678...`)

### Step 4: Create Your Configuration File

Copy the example config:

```bash
cp config.json.example config.json
```

Now edit `config.json` with your details. Here's a complete example:

```json
{
    "name": "my-ethereum",
    "default_account": "Assets:Crypto:Ethereum",
    "account_map": {
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045": "Assets:Crypto:Ethereum:MainWallet"
    },
    "fee_account": "Expenses:Crypto:GasFees",
    "expenses_account": "Expenses:Crypto:Purchases",
    "income_account": "Income:Crypto:Received",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY_HERE",
    "block_explorer_api_request_delay": 0.25,
    "base_currency": "ETH"
}
```

**Replace these values:**
- `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` → Your actual wallet address
- `YOUR_API_KEY_HERE` → Your Etherscan API key from Step 3

**Understanding the config:**

| Field | What It Means | Example |
|-------|---------------|---------|
| `name` | Output filename (creates `my-ethereum.json`) | `"my-ethereum"` |
| `account_map` | Maps your wallet addresses to Beancount account names | See above |
| `fee_account` | Where gas fees are recorded | `"Expenses:Crypto:GasFees"` |
| `expenses_account` | Where outgoing ETH goes (to unknown addresses) | `"Expenses:Crypto:Purchases"` |
| `income_account` | Where incoming ETH comes from (unknown sources) | `"Income:Crypto:Received"` |
| `block_explorer_api_key` | Your Etherscan API key | `"ABCD1234..."` |
| `block_explorer_api_request_delay` | Wait time between API calls (seconds) | `0.25` |

### Step 5: Download Your Transactions

Run the downloader to fetch your transaction history:

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

This creates a `downloads/` folder with a JSON file containing all your transactions:
```
downloads/
└── my-ethereum.json    # Your transaction data
```

### Step 6: Create the Import Script

Copy the example import script:

```bash
cp import_config.py.example import_config.py
```

The file should look like this:

```python
#!/usr/bin/env python3
"""
Beangulp import configuration for Ethereum transactions.

Usage:
    python import_config.py identify downloads/
    python import_config.py extract downloads/
"""
import os
import sys

# Add current directory to Python path (needed when running without pip install)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import beangulp
import beancount_ethereum

# Create the importer with your config
# max_delta=365 means: import transactions from the last 365 days
importers = [
    beancount_ethereum.Importer(
        config_path='config.json',
        max_delta=365
    ),
]

# This runs the beangulp command-line interface
if __name__ == '__main__':
    ingest = beangulp.Ingest(importers)
    ingest()
```

### Step 7: Test That Everything Works

First, verify the importer recognizes your downloaded file:

```bash
python import_config.py identify downloads/
```

You should see output like:
```
/path/to/downloads/my-ethereum.json
  ethereum    Assets:Crypto:Ethereum
```

### Step 8: Extract Your Transactions

Now convert your transactions to Beancount format:

```bash
python import_config.py extract downloads/
```

This prints Beancount transactions to your terminal. To save them to a file:

```bash
python import_config.py extract downloads/ > ethereum-transactions.beancount
```

### Step 9: View Your Transactions

Open `ethereum-transactions.beancount` to see your transactions:

```beancount
2024-01-15 * "0x1a2b3c4d..."
  txid: "0xabc123def456..."
  Assets:Crypto:Ethereum:MainWallet:ETH    -1.5 ETH
  Expenses:Crypto:Purchases                 1.5 ETH
  Assets:Crypto:Ethereum:MainWallet:ETH    -0.002 ETH
  Expenses:Crypto:GasFees                   0.002 ETH
```

**What this means:**
- You sent 1.5 ETH to address `0x1a2b3c4d...`
- You paid 0.002 ETH in gas fees
- The `txid` metadata links back to the blockchain transaction

---

## Complete Working Example

Here's a full example with a real (public) Ethereum address:

### 1. Create `config.json`:

```json
{
    "name": "vitalik",
    "default_account": "Assets:Crypto:Ethereum",
    "account_map": {
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045": "Assets:Crypto:Ethereum:Vitalik"
    },
    "fee_account": "Expenses:Crypto:GasFees",
    "expenses_account": "Expenses:Crypto:Sent",
    "income_account": "Income:Crypto:Received",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY",
    "block_explorer_api_request_delay": 0.25,
    "base_currency": "ETH"
}
```

### 2. Create `import_config.py`:

```python
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import beangulp
import beancount_ethereum

importers = [
    beancount_ethereum.Importer(config_path='config.json', max_delta=30),
]

if __name__ == '__main__':
    ingest = beangulp.Ingest(importers)
    ingest()
```

### 3. Download and import:

```bash
# Download transactions
python -m beancount_ethereum --config=config.json --output-dir=downloads

# Check it works
python import_config.py identify downloads/

# Extract transactions
python import_config.py extract downloads/ > transactions.beancount

# View the result
cat transactions.beancount
```

---

## Using with Your Existing Beancount Ledger

If you already have a Beancount ledger, here's how to integrate:

### 1. Create your ledger file (`ledger.beancount`):

```beancount
; Commodity declarations
1970-01-01 commodity ETH
  name: "Ethereum"

1970-01-01 commodity USDC
  name: "USD Coin"

; Account declarations
2020-01-01 open Assets:Crypto:Ethereum:MainWallet ETH, USDC
2020-01-01 open Assets:Crypto:Ethereum:MainWallet:ETH ETH
2020-01-01 open Assets:Crypto:Ethereum:MainWallet:USDC USDC
2020-01-01 open Expenses:Crypto:GasFees ETH
2020-01-01 open Expenses:Crypto:Purchases
2020-01-01 open Income:Crypto:Received

; Include imported transactions
include "ethereum-transactions.beancount"
```

### 2. Import with deduplication:

When you have existing transactions, use `-e` to avoid duplicates:

```bash
python import_config.py extract -e ledger.beancount downloads/ > new-transactions.beancount
```

This skips any transactions that already exist in your ledger (matched by `txid`).

### 3. Validate your ledger:

```bash
bean-check ledger.beancount
```

---

## Tracking Multiple Wallets

Add multiple addresses to your `account_map`:

```json
{
    "name": "all-wallets",
    "account_map": {
        "0xWallet1Address": "Assets:Crypto:Ethereum:HotWallet",
        "0xWallet2Address": "Assets:Crypto:Ethereum:ColdStorage",
        "0xWallet3Address": "Assets:Crypto:Ethereum:DeFi"
    },
    "fee_account": "Expenses:Crypto:GasFees",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY",
    "block_explorer_api_request_delay": 0.25,
    "base_currency": "ETH"
}
```

When you transfer between your own wallets, the importer recognizes both addresses and creates proper transfers:

```beancount
2024-01-15 *
  txid: "0x..."
  Assets:Crypto:Ethereum:HotWallet:ETH     -1.0 ETH
  Assets:Crypto:Ethereum:ColdStorage:ETH    1.0 ETH
  Assets:Crypto:Ethereum:HotWallet:ETH     -0.001 ETH
  Expenses:Crypto:GasFees                   0.001 ETH
```

---

## Tracking ERC-20 Tokens (USDC, USDT, etc.)

The importer automatically downloads ERC-20 token transfers. Use `currency_map` to customize how they appear:

```json
{
    "name": "mainnet",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Ethereum:Main"
    },
    "fee_account": "Expenses:Crypto:GasFees",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY",
    "base_currency": "ETH",
    "currency_map": {
        "USDC": {
            "commodity": "USDC",
            "account_suffix": "USDC"
        },
        "USDT": {
            "commodity": "USDT",
            "account_suffix": "USDT"
        },
        "WETH": {
            "commodity": "WETH",
            "account_suffix": "WETH"
        }
    }
}
```

This creates transactions like:

```beancount
2024-01-15 *
  txid: "0x..."
  Assets:Crypto:Ethereum:Main:USDC    -1000 USDC
  Expenses:Crypto:Other                1000 USDC
```

---

## Using Other Blockchains

This tool works with any Etherscan-compatible API. Here are common ones:

### Polygon (MATIC)

```json
{
    "name": "polygon",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Polygon:Main"
    },
    "block_explorer_api_url": "https://api.polygonscan.com/api",
    "block_explorer_api_key": "YOUR_POLYGONSCAN_KEY",
    "base_currency": "MATIC",
    ...
}
```

### Arbitrum

```json
{
    "name": "arbitrum",
    "block_explorer_api_url": "https://api.arbiscan.io/api",
    "block_explorer_api_key": "YOUR_ARBISCAN_KEY",
    "base_currency": "ETH",
    ...
}
```

### Base

```json
{
    "name": "base",
    "block_explorer_api_url": "https://api.basescan.org/api",
    "block_explorer_api_key": "YOUR_BASESCAN_KEY",
    "base_currency": "ETH",
    ...
}
```

### Optimism

```json
{
    "name": "optimism",
    "block_explorer_api_url": "https://api-optimistic.etherscan.io/api",
    "block_explorer_api_key": "YOUR_OPTIMISM_KEY",
    "base_currency": "ETH",
    ...
}
```

---

## Command Reference

### Download Transactions

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

Options:
- `--config` / `-c`: Path to your config file
- `--output-dir` / `-o`: Where to save the downloaded JSON

### Identify Files

```bash
python import_config.py identify downloads/
```

Shows which files the importer recognizes.

### Extract Transactions

```bash
# Print to terminal
python import_config.py extract downloads/

# Save to file
python import_config.py extract downloads/ > output.beancount

# Deduplicate against existing ledger
python import_config.py extract -e ledger.beancount downloads/
```

---

## Troubleshooting

### "No transactions found"

1. Check your wallet address is correct (copy directly from Etherscan)
2. Verify your API key works by visiting: `https://api.etherscan.io/api?module=account&action=txlist&address=YOUR_ADDRESS&apikey=YOUR_KEY`
3. Make sure `max_delta` is large enough to include your transactions

### "Rate limit exceeded"

Increase the delay between API requests:

```json
{
    "block_explorer_api_request_delay": 0.5
}
```

Free Etherscan accounts allow 5 requests/second, so 0.25 seconds delay is safe.

### Old transactions not appearing

The importer only imports transactions from the last 90 days by default. Increase `max_delta`:

```python
beancount_ethereum.Importer(config_path='config.json', max_delta=3650)  # 10 years
```

### Transactions appearing twice

Use the `-e` flag to deduplicate:

```bash
python import_config.py extract -e ledger.beancount downloads/
```

---

## Configuration Reference

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `name` | Yes | - | Output filename (e.g., `"mainnet"` → `mainnet.json`) |
| `default_account` | No | `"Assets:Crypto:ETH"` | Default account for beangulp |
| `account_map` | Yes | - | Wallet address → Beancount account mapping |
| `fee_account` | Yes | - | Account for gas fees |
| `expenses_account` | Yes | - | Account for outgoing transactions |
| `income_account` | Yes | - | Account for incoming transactions |
| `block_explorer_api_url` | Yes | - | API endpoint URL |
| `block_explorer_api_key` | No | - | API key (required for Etherscan) |
| `block_explorer_api_request_delay` | No | `0` | Delay between API calls (seconds) |
| `base_currency` | No | `"ETH"` | Native currency symbol |
| `currency_map` | No | - | Token symbol mappings |

---

## Testing

Run the test suite to verify everything works:

```bash
pip install pytest pytest-cov
PYTHONPATH=. pytest tests/ -v
```

---

## License

GPL-3.0
