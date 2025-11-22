"""Pytest fixtures for beancount-ethereum tests."""

import datetime
import json
import os
import tempfile

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def base_config():
    """Return a base configuration dictionary."""
    return {
        'name': 'test',
        'default_account': 'Assets:Crypto:ETH',
        'account_map': {
            '0xabc123def456789': 'Assets:Ethereum:Wallet1',
            '0x987654321fedcba': 'Assets:Ethereum:Wallet2',
        },
        'fee_account': 'Expenses:Crypto:Fees',
        'expenses_account': 'Expenses:Crypto:Other',
        'income_account': 'Income:Crypto:Other',
        'base_currency': 'ETH',
        'block_explorer_api_url': 'https://api.etherscan.io/api',
        'block_explorer_api_key': 'TEST_API_KEY',
    }


@pytest.fixture
def config_with_currency_map(base_config):
    """Return a configuration with currency mapping."""
    base_config['currency_map'] = {
        'USDC': {'commodity': 'USD', 'account_suffix': 'USDC'},
        'WETH': {'commodity': 'ETH'},
    }
    return base_config


@pytest.fixture
def config_file(temp_dir, base_config):
    """Create a config file and return its path."""
    config_path = os.path.join(temp_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(base_config, f)
    return config_path


@pytest.fixture
def recent_timestamp():
    """Return a recent timestamp (yesterday)."""
    return int(datetime.datetime.now().timestamp()) - 86400


@pytest.fixture
def sample_transactions(recent_timestamp):
    """Return sample transaction data."""
    return [
        {
            'tx_id': '0xhash1',
            'time': recent_timestamp,
            'from': '0xabc123def456789',
            'to': '0xexternal_address',
            'currency': 'ETH',
            'value': '1.5',
        },
        {
            'tx_id': '0xhash1',
            'time': recent_timestamp,
            'from': '0xabc123def456789',
            'to': '0xffffffffffffffffffffffffffffffffffffffff',  # Miner (fee)
            'currency': 'ETH',
            'value': '0.001',
        },
    ]


@pytest.fixture
def transactions_file(temp_dir, sample_transactions):
    """Create a transactions file and return its path."""
    tx_path = os.path.join(temp_dir, 'test.json')
    with open(tx_path, 'w') as f:
        json.dump(sample_transactions, f)
    return tx_path
