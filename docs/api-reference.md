# API Reference

This document provides detailed API documentation for all public classes and functions in beancount-ethereum.

## Table of Contents

- [Importer Module](#importer-module)
  - [Importer Class](#importer-class)
- [Downloader Module](#downloader-module)
  - [BlockExplorerApi Class](#blockexplorerapi-class)
  - [download Function](#download-function)
- [Constants](#constants)

---

## Importer Module

`beancount_ethereum.importer`

### Importer Class

The main importer class that converts downloaded Ethereum transactions into Beancount entries.

```python
from beancount_ethereum import Importer
```

#### Constructor

```python
Importer(config_path='config.json', max_delta=90)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `str` | `'config.json'` | Path to the JSON configuration file |
| `max_delta` | `int` | `90` | Maximum age of transactions in days to import |

**Example:**

```python
# Import transactions from the last 90 days
importer = Importer(config_path='config.json')

# Import transactions from the last year
importer = Importer(config_path='config.json', max_delta=365)

# Import all transactions (very large max_delta)
importer = Importer(config_path='config.json', max_delta=3650)
```

#### Methods

##### `name() -> str`

Returns the name of this importer.

**Returns:** `'ethereum'`

**Example:**

```python
importer = Importer(config_path='config.json')
print(importer.name())  # Output: 'ethereum'
```

##### `identify(filepath: str) -> bool`

Determines if the given file should be handled by this importer.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | `str` | Path to the file to check |

**Returns:** `True` if the filename matches `{name}.json` from config, `False` otherwise.

**Example:**

```python
importer = Importer(config_path='config.json')  # config has name: "mainnet"
importer.identify('/path/to/mainnet.json')  # Returns: True
importer.identify('/path/to/other.json')    # Returns: False
```

##### `account(filepath: str) -> str`

Returns the primary account associated with this importer.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | `str` | Path to the file (not used, but required by beangulp) |

**Returns:** The `default_account` from config, or `'Assets:Crypto:ETH'` if not set.

**Example:**

```python
importer = Importer(config_path='config.json')
print(importer.account('/path/to/file.json'))  # Output: 'Assets:Crypto:ETH'
```

##### `extract(filepath: str, existing_entries=None) -> list`

Extracts Beancount transactions from the downloaded JSON file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filepath` | `str` | Path to the transactions JSON file |
| `existing_entries` | `list` or `None` | Existing Beancount entries for deduplication |

**Returns:** List of `beancount.core.data.Transaction` objects.

**Behavior:**

1. Loads transactions from the JSON file
2. Filters out transactions older than `max_delta` days
3. Filters out transactions that already exist in `existing_entries` (by `txid` metadata)
4. Groups transfers by transaction ID
5. Creates postings for each transfer

**Example:**

```python
importer = Importer(config_path='config.json', max_delta=365)

# Extract without deduplication
entries = importer.extract('/path/to/mainnet.json')

# Extract with deduplication
from beancount import loader
existing, errors, options = loader.load_file('ledger.beancount')
entries = importer.extract('/path/to/mainnet.json', existing_entries=existing)
```

#### Properties

##### `account_map -> dict`

Returns the account mapping with lowercased addresses.

**Returns:** Dictionary mapping lowercased Ethereum addresses to Beancount account names.

---

## Downloader Module

`beancount_ethereum.downloader`

### BlockExplorerApi Class

Client for interacting with Etherscan-compatible block explorer APIs.

```python
from beancount_ethereum.downloader import BlockExplorerApi
```

#### Constructor

```python
BlockExplorerApi(api_url: str, api_key: str, delay: float = 0.0, base_currency: str = 'ETH')
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_url` | `str` | Required | Base URL for the API (e.g., `'https://api.etherscan.io/api'`) |
| `api_key` | `str` | Required | API key for authentication (can be `None` for some explorers) |
| `delay` | `float` | `0.0` | Minimum delay between requests in seconds |
| `base_currency` | `str` | `'ETH'` | Symbol for the native currency |

**Example:**

```python
# Etherscan Mainnet
api = BlockExplorerApi(
    api_url='https://api.etherscan.io/api',
    api_key='YOUR_API_KEY',
    delay=0.2  # Rate limit: 5 requests per second
)

# Polygon
api = BlockExplorerApi(
    api_url='https://api.polygonscan.com/api',
    api_key='YOUR_API_KEY',
    base_currency='MATIC'
)

# Blockscout (no API key needed)
api = BlockExplorerApi(
    api_url='https://blockscout.com/xdai/mainnet/api',
    api_key=None,
    base_currency='xDAI'
)
```

#### Methods

##### `get_normal_transactions(address: str) -> list`

Fetches normal (external) transactions for an address.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | `str` | Ethereum address to query |

**Returns:** List of transaction dictionaries with keys:
- `tx_id`: Transaction hash
- `time`: Unix timestamp
- `from`: Sender address
- `to`: Recipient address
- `currency`: Currency symbol
- `value`: Decimal value

**Note:** Also returns fee transactions (to the miner address) for transactions sent from the address.

##### `get_internal_transactions(address: str) -> list`

Fetches internal transactions (contract calls) for an address.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | `str` | Ethereum address to query |

**Returns:** List of transaction dictionaries (same format as `get_normal_transactions`).

##### `get_erc20_transfers(address: str) -> list`

Fetches ERC-20 token transfers for an address.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | `str` | Ethereum address to query |

**Returns:** List of transaction dictionaries with the `currency` field set to the token symbol.

**Note:** NFT transfers (empty `tokenDecimal`) are automatically skipped.

---

### download Function

```python
download(config: dict, output_dir: str)
```

Downloads all transactions for addresses in the config and saves to a JSON file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `dict` | Configuration dictionary |
| `output_dir` | `str` | Directory to save the output file |

**Behavior:**

1. Creates a `BlockExplorerApi` instance from config
2. For each address in `account_map`:
   - Fetches normal transactions
   - Fetches internal transactions
   - Fetches ERC-20 transfers
3. Saves all transactions to `{output_dir}/{name}.json`

**Example:**

```python
from beancount_ethereum.downloader import download

config = {
    'name': 'mainnet',
    'account_map': {'0x123...': 'Assets:ETH'},
    'block_explorer_api_url': 'https://api.etherscan.io/api',
    'block_explorer_api_key': 'YOUR_KEY',
}

download(config, './downloads')
# Creates: ./downloads/mainnet.json
```

---

## Constants

### DEFAULT_CURRENCY

```python
DEFAULT_CURRENCY = 'ETH'
```

Default currency symbol used when not specified in config.

### MINER

```python
MINER = '0xffffffffffffffffffffffffffffffffffffffff'
```

Special address used to represent transaction fee payments.

### WEI

```python
WEI = 10 ** 18
```

Conversion factor from Wei to Ether.

### NO_TRANSACTIONS

```python
NO_TRANSACTIONS = [
    'No transactions found',
    'No internal transactions found',
    'No token transfers found',
]
```

API response messages indicating empty results (not errors).
