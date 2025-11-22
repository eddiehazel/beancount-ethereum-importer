# Advanced Usage Guide

This guide covers advanced configuration and usage scenarios for beancount-ethereum.

## Table of Contents

- [Multi-Chain Setup](#multi-chain-setup)
- [Currency Mapping](#currency-mapping)
- [Custom Workflows](#custom-workflows)
- [Integration with Fava](#integration-with-fava)
- [Automation](#automation)
- [Handling Edge Cases](#handling-edge-cases)

---

## Multi-Chain Setup

You can track transactions across multiple EVM-compatible chains by creating separate configurations for each.

### Example: Ethereum + Polygon + Arbitrum

**config-ethereum.json:**
```json
{
    "name": "ethereum",
    "default_account": "Assets:Crypto:Ethereum",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Ethereum:Main"
    },
    "fee_account": "Expenses:Crypto:Fees:Ethereum",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_ETHERSCAN_KEY",
    "base_currency": "ETH"
}
```

**config-polygon.json:**
```json
{
    "name": "polygon",
    "default_account": "Assets:Crypto:Polygon",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Polygon:Main"
    },
    "fee_account": "Expenses:Crypto:Fees:Polygon",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.polygonscan.com/api",
    "block_explorer_api_key": "YOUR_POLYGONSCAN_KEY",
    "base_currency": "MATIC"
}
```

**config-arbitrum.json:**
```json
{
    "name": "arbitrum",
    "default_account": "Assets:Crypto:Arbitrum",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Arbitrum:Main"
    },
    "fee_account": "Expenses:Crypto:Fees:Arbitrum",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.arbiscan.io/api",
    "block_explorer_api_key": "YOUR_ARBISCAN_KEY",
    "base_currency": "ETH"
}
```

**import_config.py:**
```python
#!/usr/bin/env python3
import beangulp
import beancount_ethereum

importers = [
    beancount_ethereum.Importer(config_path='config-ethereum.json', max_delta=365),
    beancount_ethereum.Importer(config_path='config-polygon.json', max_delta=365),
    beancount_ethereum.Importer(config_path='config-arbitrum.json', max_delta=365),
]

if __name__ == '__main__':
    ingest = beangulp.Ingest(importers)
    ingest()
```

**Download script:**
```bash
#!/bin/bash
python -m beancount_ethereum --config=config-ethereum.json --output-dir=downloads
python -m beancount_ethereum --config=config-polygon.json --output-dir=downloads
python -m beancount_ethereum --config=config-arbitrum.json --output-dir=downloads
```

---

## Currency Mapping

Use currency mapping to:
- Convert stablecoins to their underlying currency for reporting
- Use custom account suffixes for different tokens
- Handle wrapped tokens

### Stablecoin Mapping

Map USDC and USDT to USD for cleaner reporting:

```json
{
    "currency_map": {
        "USDC": {"commodity": "USD", "account_suffix": "USDC"},
        "USDT": {"commodity": "USD", "account_suffix": "USDT"},
        "DAI": {"commodity": "USD", "account_suffix": "DAI"}
    }
}
```

This produces postings like:
```beancount
Assets:Ethereum:Wallet:USDC  100 USD
```

### Wrapped Token Mapping

Map wrapped ETH to ETH:

```json
{
    "currency_map": {
        "WETH": {"commodity": "ETH"},
        "stETH": {"commodity": "ETH", "account_suffix": "stETH"},
        "wstETH": {"commodity": "ETH", "account_suffix": "wstETH"}
    }
}
```

### Full Example

```json
{
    "name": "mainnet",
    "account_map": {
        "0xYourAddress": "Assets:Crypto:Ethereum"
    },
    "fee_account": "Expenses:Crypto:Fees",
    "expenses_account": "Expenses:Crypto:Other",
    "income_account": "Income:Crypto:Other",
    "block_explorer_api_url": "https://api.etherscan.io/api",
    "block_explorer_api_key": "YOUR_KEY",
    "base_currency": "ETH",
    "currency_map": {
        "USDC": {"commodity": "USD", "account_suffix": "USDC"},
        "USDT": {"commodity": "USD", "account_suffix": "USDT"},
        "DAI": {"commodity": "USD", "account_suffix": "DAI"},
        "WETH": {"commodity": "ETH"},
        "WBTC": {"commodity": "BTC", "account_suffix": "WBTC"},
        "stETH": {"commodity": "ETH", "account_suffix": "stETH"}
    }
}
```

---

## Custom Workflows

### Programmatic Usage

Use the importer programmatically for custom workflows:

```python
import json
from beancount.parser import printer
from beancount_ethereum import Importer
from beancount_ethereum.downloader import download

# Download transactions
with open('config.json') as f:
    config = json.load(f)

download(config, 'downloads')

# Import and process
importer = Importer(config_path='config.json', max_delta=365)
entries = importer.extract('downloads/mainnet.json')

# Filter for large transactions only
large_txs = [e for e in entries
             if any(abs(p.units.number) > 1 for p in e.postings)]

# Print to stdout
for entry in large_txs:
    print(printer.format_entry(entry))
```

### Custom Post-Processing

Add custom metadata or modify transactions:

```python
from beancount.core.data import TxnPosting
from beancount_ethereum import Importer

importer = Importer(config_path='config.json')
entries = importer.extract('downloads/mainnet.json')

# Add custom tags
processed = []
for entry in entries:
    # Add a tag for transactions over 1 ETH
    total_value = sum(abs(p.units.number) for p in entry.postings
                      if p.units.currency == 'ETH')
    if total_value > 1:
        entry = entry._replace(tags=entry.tags | {'large-transaction'})
    processed.append(entry)
```

---

## Integration with Fava

### Basic Setup

1. Import transactions to a file:
```bash
python import_config.py extract -e ledger.beancount downloads/ > ethereum.beancount
```

2. Include in your main ledger:
```beancount
include "ethereum.beancount"
```

3. Run Fava:
```bash
fava ledger.beancount
```

### Commodity Declarations

Add these to your ledger for proper display in Fava:

```beancount
1970-01-01 commodity ETH
  name: "Ethereum"

1970-01-01 commodity MATIC
  name: "Polygon"

1970-01-01 commodity USDC
  name: "USD Coin"

1970-01-01 commodity WETH
  name: "Wrapped Ether"
```

### Account Declarations

```beancount
2020-01-01 open Assets:Crypto:Ethereum:Main ETH, USDC, WETH
2020-01-01 open Assets:Crypto:Ethereum:Main:USDC USD
2020-01-01 open Expenses:Crypto:Fees ETH
2020-01-01 open Expenses:Crypto:Other
2020-01-01 open Income:Crypto:Other
```

---

## Automation

### Cron Job for Daily Updates

Create a script `update-ethereum.sh`:

```bash
#!/bin/bash
set -e

cd /path/to/your/beancount

# Download latest transactions
python -m beancount_ethereum --config=config.json --output-dir=downloads

# Extract and append new transactions
python import_config.py extract -e ledger.beancount downloads/ >> ethereum.beancount

# Validate the ledger
bean-check ledger.beancount

echo "Updated at $(date)"
```

Add to crontab:
```bash
0 6 * * * /path/to/update-ethereum.sh >> /var/log/beancount-update.log 2>&1
```

### GitHub Actions Workflow

```yaml
name: Update Ethereum Transactions

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install beancount beangulp beancount-ethereum

      - name: Download transactions
        env:
          ETHERSCAN_API_KEY: ${{ secrets.ETHERSCAN_API_KEY }}
        run: |
          # Update config with API key
          jq '.block_explorer_api_key = env.ETHERSCAN_API_KEY' config.json > config-ci.json
          python -m beancount_ethereum --config=config-ci.json --output-dir=downloads

      - name: Extract transactions
        run: |
          python import_config.py extract -e ledger.beancount downloads/ > new-transactions.beancount

      - name: Commit changes
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add downloads/ new-transactions.beancount
          git commit -m "Update Ethereum transactions" || exit 0
          git push
```

---

## Handling Edge Cases

### Failed Transactions

Failed transactions don't transfer value but still charge gas. The importer handles this by:
- Skipping the value transfer (since it didn't happen)
- Still recording the gas fee

### Contract Interactions

When interacting with contracts:
- Normal transactions show ETH sent to the contract
- Internal transactions show ETH sent back from the contract
- Token transfers show ERC-20 movements

### Missing Data

If transactions are missing:

1. Check if the address is correct (case-insensitive)
2. Verify the API key is valid
3. Check if the block explorer indexes that transaction type
4. Try increasing `max_delta` for older transactions

### Duplicate Handling

The importer deduplicates by transaction ID (`txid` metadata). If you see duplicates:

1. Ensure you're passing existing entries to `extract()`
2. Check that `txid` metadata is preserved in your ledger

### Rate Limiting

If you hit rate limits:

```json
{
    "block_explorer_api_request_delay": 0.25
}
```

For free Etherscan accounts, 0.2-0.25 seconds delay is recommended (5 requests/second limit).

### Large Wallets

For wallets with many transactions:

1. Use a paid API plan for higher limits
2. Download in batches by adjusting `max_delta`
3. Consider archiving old transactions to separate files
