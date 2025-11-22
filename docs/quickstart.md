# Quickstart Guide

Get your Ethereum transactions into Beancount in 5 minutes.

## What You'll Need

1. **Python 3.9+** - Check with `python --version`
2. **Your wallet address** - e.g., `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
3. **Etherscan API key** - Free from [etherscan.io/myapikey](https://etherscan.io/myapikey)

## Step 1: Install (30 seconds)

```bash
# Install dependencies
pip install beancount beangulp

# Get the code
git clone https://github.com/xuhcc/beancount-ethereum-importer.git
cd beancount-ethereum-importer
```

## Step 2: Configure (1 minute)

Create `config.json`:

```json
{
    "name": "ethereum",
    "default_account": "Assets:Crypto:Ethereum",
    "account_map": {
        "YOUR_WALLET_ADDRESS": "Assets:Crypto:Ethereum:Main"
    },
    "fee_account": "Expenses:Crypto:GasFees",
    "expenses_account": "Expenses:Crypto:Purchases",
    "income_account": "Income:Crypto:Received",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_API_KEY",
    "block_explorer_api_request_delay": 0.25,
    "base_currency": "ETH"
}
```

Replace:
- `YOUR_WALLET_ADDRESS` → Your actual Ethereum address
- `YOUR_API_KEY` → Your Etherscan API key

## Step 3: Download Transactions (1 minute)

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

You'll see: `Transactions saved to downloads/ethereum.json`

## Step 4: Create Import Script (30 seconds)

Create `import_config.py`:

```python
#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import beangulp
import beancount_ethereum

importers = [
    beancount_ethereum.Importer(config_path='config.json', max_delta=365),
]

if __name__ == '__main__':
    beangulp.Ingest(importers)()
```

## Step 5: Import! (30 seconds)

```bash
# Test it works
python import_config.py identify downloads/

# Extract transactions
python import_config.py extract downloads/ > transactions.beancount

# View results
cat transactions.beancount
```

## Done!

Your `transactions.beancount` now contains entries like:

```beancount
2024-01-15 * "0x1234abcd..."
  txid: "0xabc123..."
  Assets:Crypto:Ethereum:Main:ETH    -1.5 ETH
  Expenses:Crypto:Purchases           1.5 ETH
  Assets:Crypto:Ethereum:Main:ETH    -0.002 ETH
  Expenses:Crypto:GasFees             0.002 ETH
```

## What's Next?

- **Track multiple wallets**: Add more addresses to `account_map`
- **Track tokens**: Add `currency_map` for USDC, USDT, etc.
- **Other chains**: Use Polygon, Arbitrum, Base with different API URLs
- **Automate**: Set up a cron job to update daily

See the [README](../README.md) for complete documentation.
