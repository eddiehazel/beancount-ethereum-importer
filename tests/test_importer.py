"""Tests for the Ethereum importer."""

import datetime
import json
import os

import pytest
from beancount.core.data import Transaction

from beancount_ethereum.importer import Importer, DEFAULT_CURRENCY, MINER


class TestImporterInitialization:
    """Tests for Importer initialization."""

    def test_init_loads_config(self, config_file, base_config):
        """Test that __init__ loads the config file correctly."""
        importer = Importer(config_path=config_file)
        assert importer.config['name'] == base_config['name']
        assert importer.config['fee_account'] == base_config['fee_account']

    def test_init_sets_min_date(self, config_file):
        """Test that __init__ sets min_date based on max_delta."""
        importer = Importer(config_path=config_file, max_delta=30)
        expected_min = datetime.datetime.now() - datetime.timedelta(days=30)
        # Allow 1 second tolerance
        assert abs((importer.min_date - expected_min).total_seconds()) < 1

    def test_init_default_max_delta(self, config_file):
        """Test that default max_delta is 90 days."""
        importer = Importer(config_path=config_file)
        expected_min = datetime.datetime.now() - datetime.timedelta(days=90)
        assert abs((importer.min_date - expected_min).total_seconds()) < 1


class TestImporterIdentify:
    """Tests for the identify() method."""

    def test_identify_matching_file(self, config_file, temp_dir):
        """Test identify returns True for matching filename."""
        importer = Importer(config_path=config_file)
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump([], f)
        assert importer.identify(tx_file) is True

    def test_identify_non_matching_file(self, config_file, temp_dir):
        """Test identify returns False for non-matching filename."""
        importer = Importer(config_path=config_file)
        tx_file = os.path.join(temp_dir, 'other.json')
        with open(tx_file, 'w') as f:
            json.dump([], f)
        assert importer.identify(tx_file) is False

    def test_identify_different_extension(self, config_file, temp_dir):
        """Test identify returns False for different extension."""
        importer = Importer(config_path=config_file)
        tx_file = os.path.join(temp_dir, 'test.csv')
        assert importer.identify(tx_file) is False


class TestImporterAccount:
    """Tests for the account() method."""

    def test_account_returns_default(self, config_file, transactions_file):
        """Test account returns the default_account from config."""
        importer = Importer(config_path=config_file)
        assert importer.account(transactions_file) == 'Assets:Crypto:ETH'

    def test_account_fallback(self, temp_dir):
        """Test account falls back when default_account not in config."""
        config = {'name': 'test', 'account_map': {}}
        config_path = os.path.join(temp_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        importer = Importer(config_path=config_path)
        assert importer.account('/any/path') == 'Assets:Crypto:ETH'


class TestImporterName:
    """Tests for the name() method."""

    def test_name_returns_ethereum(self, config_file):
        """Test name returns 'ethereum'."""
        importer = Importer(config_path=config_file)
        assert importer.name() == 'ethereum'


class TestImporterAccountMap:
    """Tests for the account_map property."""

    def test_account_map_lowercases_keys(self, config_file):
        """Test that account_map lowercases all keys."""
        importer = Importer(config_path=config_file)
        for key in importer.account_map:
            assert key == key.lower()

    def test_account_map_preserves_values(self, config_file, base_config):
        """Test that account_map preserves account values."""
        importer = Importer(config_path=config_file)
        for key, value in base_config['account_map'].items():
            assert importer.account_map[key.lower()] == value


class TestImporterCurrencyMapping:
    """Tests for currency mapping methods."""

    def test_account_suffix_with_mapping(self, temp_dir, config_with_currency_map):
        """Test account_suffix returns mapped suffix."""
        config_path = os.path.join(temp_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config_with_currency_map, f)
        importer = Importer(config_path=config_path)
        assert importer.account_suffix('USDC') == 'USDC'
        assert importer.account_suffix('WETH') == 'ETH'

    def test_account_suffix_unmapped_currency(self, temp_dir, config_with_currency_map):
        """Test account_suffix returns currency itself when not mapped."""
        config_path = os.path.join(temp_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config_with_currency_map, f)
        importer = Importer(config_path=config_path)
        assert importer.account_suffix('DAI') == 'DAI'

    def test_account_suffix_no_mapping(self, config_file):
        """Test account_suffix returns currency when no mapping exists."""
        importer = Importer(config_path=config_file)
        assert importer.account_suffix('ETH') == 'ETH'

    def test_commodity_with_mapping(self, temp_dir, config_with_currency_map):
        """Test commodity returns mapped commodity."""
        config_path = os.path.join(temp_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config_with_currency_map, f)
        importer = Importer(config_path=config_path)
        assert importer.commodity('USDC') == 'USD'
        assert importer.commodity('WETH') == 'ETH'

    def test_commodity_unmapped(self, config_file):
        """Test commodity returns currency itself when not mapped."""
        importer = Importer(config_path=config_file)
        assert importer.commodity('ETH') == 'ETH'


class TestImporterExtract:
    """Tests for the extract() method."""

    def test_extract_basic_transaction(self, config_file, transactions_file):
        """Test extracting a basic transaction."""
        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(transactions_file)

        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, Transaction)
        assert entry.meta['txid'] == '0xhash1'

    def test_extract_creates_postings(self, config_file, transactions_file):
        """Test that extract creates correct postings."""
        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(transactions_file)

        entry = entries[0]
        # Should have 4 postings: from (known), to (unknown), from (known), to (miner/fee)
        assert len(entry.postings) == 4

    def test_extract_filters_old_transactions(self, config_file, temp_dir):
        """Test that old transactions are filtered out."""
        old_timestamp = int(datetime.datetime.now().timestamp()) - (100 * 86400)
        transactions = [{
            'tx_id': '0xold',
            'time': old_timestamp,
            'from': '0xabc123def456789',
            'to': '0xdef',
            'currency': 'ETH',
            'value': '1.0',
        }]
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump(transactions, f)

        importer = Importer(config_path=config_file, max_delta=30)
        entries = importer.extract(tx_file)

        assert len(entries) == 0

    def test_extract_deduplicates_existing(self, config_file, transactions_file):
        """Test that existing transactions are skipped."""
        importer = Importer(config_path=config_file, max_delta=365)

        # Create a mock existing entry
        from beancount.core.data import new_metadata
        existing = [
            Transaction(
                new_metadata('', 0, {'txid': '0xhash1'}),
                datetime.date.today(),
                '*', '', '', frozenset(), frozenset(), []
            )
        ]

        entries = importer.extract(transactions_file, existing_entries=existing)
        assert len(entries) == 0

    def test_extract_groups_by_tx_id(self, config_file, temp_dir, recent_timestamp):
        """Test that transfers are grouped by transaction ID."""
        transactions = [
            {'tx_id': '0xhash1', 'time': recent_timestamp, 'from': '0xabc123def456789',
             'to': '0xdef', 'currency': 'ETH', 'value': '1.0'},
            {'tx_id': '0xhash1', 'time': recent_timestamp, 'from': '0xabc123def456789',
             'to': '0xffffffffffffffffffffffffffffffffffffffff', 'currency': 'ETH', 'value': '0.01'},
            {'tx_id': '0xhash2', 'time': recent_timestamp, 'from': '0xabc123def456789',
             'to': '0xghi', 'currency': 'ETH', 'value': '2.0'},
        ]
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump(transactions, f)

        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(tx_file)

        assert len(entries) == 2
        tx_ids = {e.meta['txid'] for e in entries}
        assert tx_ids == {'0xhash1', '0xhash2'}

    def test_extract_handles_known_addresses(self, config_file, temp_dir, recent_timestamp):
        """Test that known addresses use mapped accounts."""
        transactions = [{
            'tx_id': '0xhash1',
            'time': recent_timestamp,
            'from': '0xabc123def456789',
            'to': '0x987654321fedcba',
            'currency': 'ETH',
            'value': '1.0',
        }]
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump(transactions, f)

        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(tx_file)

        entry = entries[0]
        accounts = {p.account for p in entry.postings}
        assert 'Assets:Ethereum:Wallet1:ETH' in accounts
        assert 'Assets:Ethereum:Wallet2:ETH' in accounts

    def test_extract_empty_file(self, config_file, temp_dir):
        """Test extracting from an empty transactions file."""
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump([], f)

        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(tx_file)

        assert entries == []

    def test_extract_zero_value_skipped(self, config_file, temp_dir, recent_timestamp):
        """Test that zero-value transfers don't create postings."""
        transactions = [{
            'tx_id': '0xhash1',
            'time': recent_timestamp,
            'from': '0xabc123def456789',
            'to': '0xdef',
            'currency': 'ETH',
            'value': '0',
        }]
        tx_file = os.path.join(temp_dir, 'test.json')
        with open(tx_file, 'w') as f:
            json.dump(transactions, f)

        importer = Importer(config_path=config_file, max_delta=365)
        entries = importer.extract(tx_file)

        # Transaction with only zero-value transfers should still be created
        # but with no postings (or minimal postings)
        assert len(entries) == 1
        # Zero-value postings should be skipped
        for posting in entries[0].postings:
            assert posting.units.number != 0


class TestImporterIntegration:
    """Integration tests for the Importer class."""

    def test_beangulp_compatibility(self, config_file):
        """Test that Importer is compatible with beangulp."""
        from beangulp import Importer as BeangulpImporter
        importer = Importer(config_path=config_file)
        assert isinstance(importer, BeangulpImporter)

    def test_full_workflow(self, config_file, transactions_file):
        """Test a complete import workflow."""
        importer = Importer(config_path=config_file, max_delta=365)

        # Identify
        assert importer.identify(transactions_file)

        # Get account
        account = importer.account(transactions_file)
        assert account is not None

        # Extract
        entries = importer.extract(transactions_file)
        assert len(entries) > 0

        # Verify entry structure
        for entry in entries:
            assert isinstance(entry, Transaction)
            assert 'txid' in entry.meta
            assert len(entry.postings) > 0
