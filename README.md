# Ethereum transaction importer for Beancount

## Requirements

- Python >= 3.9
- Beancount 3.x
- Beangulp

## Configuration

Example of configuration file: [config.json](config.json.example).

`beancount-ethereum` can load data from [Etherscan](https://etherscan.io/) or block explorers with similar API like [Blockscout](https://blockscout.com/poa/xdai/).

If you are using Etherscan, get your API key at https://etherscan.io/.

## Install

Install `beancount-ethereum`:

```
pip install beancount-ethereum
```

To install from source:

```
pip install -e .
```

### Running Locally Without pip Install

If you want to run the code directly from the repository without installing via pip:

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
# Edit config.json with your Etherscan API key and wallet addresses
```

4. Download transactions using the module directly:

```bash
python -m beancount_ethereum --config=config.json --output-dir=downloads
```

5. Run the importer with PYTHONPATH set:

```bash
# Identify files
PYTHONPATH=. python import_config.py identify downloads/

# Extract transactions
PYTHONPATH=. python import_config.py extract downloads/

# Extract with deduplication against existing ledger
PYTHONPATH=. python import_config.py extract -e ledger.beancount downloads/
```

Alternatively, you can export PYTHONPATH once for your session:

```bash
export PYTHONPATH=/path/to/beancount-ethereum-importer
python import_config.py identify downloads/
```

## Usage

Download transactions to file:

```
beancount-ethereum --config=config.json --output-dir=downloads
```

### Importing with Beangulp

Create an import configuration script ([example](import_config.py.example)):

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

Check with identify:

```
python import_config.py identify downloads/
```

Import transactions with extract:

```
python import_config.py extract downloads/
```

To deduplicate against existing entries:

```
python import_config.py extract -e ledger.beancount downloads/
```

## Deploy

Deploy `beancount-ethereum`:

```
make deploy
```
