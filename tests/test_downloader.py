"""Tests for the Ethereum transaction downloader."""

import json
import os
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from beancount_ethereum.downloader import (
    BlockExplorerApi,
    download,
    DEFAULT_CURRENCY,
    MINER,
    WEI,
    NO_TRANSACTIONS,
)


class TestBlockExplorerApiInit:
    """Tests for BlockExplorerApi initialization."""

    def test_init_stores_params(self):
        """Test that __init__ stores all parameters correctly."""
        api = BlockExplorerApi(
            api_url='https://api.etherscan.io/api',
            api_key='TEST_KEY',
            delay=0.5,
            base_currency='ETH',
        )
        assert api.api_url == 'https://api.etherscan.io/api'
        assert api.api_key == 'TEST_KEY'
        assert api.delay == 0.5
        assert api.base_currency == 'ETH'

    def test_init_default_values(self):
        """Test default values for optional parameters."""
        api = BlockExplorerApi(
            api_url='https://api.etherscan.io/api',
            api_key='TEST_KEY',
        )
        assert api.delay == 0.0
        assert api.base_currency == DEFAULT_CURRENCY


class TestBlockExplorerApiRequest:
    """Tests for the _make_api_request method."""

    @patch('beancount_ethereum.downloader.urlopen')
    def test_make_api_request_success(self, mock_urlopen):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{'hash': '0xabc'}]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        result = api._make_api_request('0xaddress', 'txlist')

        assert result == [{'hash': '0xabc'}]
        mock_urlopen.assert_called_once()

    @patch('beancount_ethereum.downloader.urlopen')
    def test_make_api_request_no_transactions(self, mock_urlopen):
        """Test API request with no transactions."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '0',
            'message': 'No transactions found',
            'result': []
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        result = api._make_api_request('0xaddress', 'txlist')

        assert result == []

    @patch('beancount_ethereum.downloader.urlopen')
    def test_make_api_request_error(self, mock_urlopen):
        """Test API request with error response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '0',
            'message': 'NOTOK',
            'result': 'Error message'
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')

        with pytest.raises(RuntimeError):
            api._make_api_request('0xaddress', 'txlist')

    @patch('beancount_ethereum.downloader.urlopen')
    @patch('time.sleep')
    def test_make_api_request_respects_delay(self, mock_sleep, mock_urlopen):
        """Test that requests respect the delay setting."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': []
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY', delay=1.0)

        # First request - no delay needed
        api._make_api_request('0xaddress', 'txlist')

        # Second request immediately - should delay
        api._make_api_request('0xaddress', 'txlist')

        # Sleep should have been called for the delay
        assert mock_sleep.called

    @patch('beancount_ethereum.downloader.urlopen')
    def test_make_api_request_no_api_key(self, mock_urlopen):
        """Test request without API key."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': []
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', api_key=None)
        api._make_api_request('0xaddress', 'txlist')

        # Verify the URL doesn't contain apikey parameter
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        assert 'apikey' not in request.full_url


class TestGetNormalTransactions:
    """Tests for get_normal_transactions method."""

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_normal_transactions(self, mock_urlopen):
        """Test fetching normal transactions."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'hash': '0xhash1',
                'timeStamp': '1700000000',
                'from': '0xfrom',
                'to': '0xto',
                'value': '1000000000000000000',  # 1 ETH
                'gasUsed': '21000',
                'gasPrice': '50000000000',  # 50 gwei
                'isError': '0',
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_normal_transactions('0xfrom')

        # Should have 2 transactions: the transfer and the fee
        assert len(transactions) == 2

        # First is the transfer
        tx = transactions[0]
        assert tx['tx_id'] == '0xhash1'
        assert tx['from'] == '0xfrom'
        assert tx['to'] == '0xto'
        assert tx['value'] == Decimal('1')
        assert tx['currency'] == 'ETH'

        # Second is the fee
        fee_tx = transactions[1]
        assert fee_tx['to'] == MINER
        assert fee_tx['value'] == Decimal('21000') * Decimal('50000000000') / WEI

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_normal_transactions_skips_errors(self, mock_urlopen):
        """Test that failed transactions are skipped."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'hash': '0xhash1',
                'timeStamp': '1700000000',
                'from': '0xfrom',
                'to': '0xto',
                'value': '1000000000000000000',
                'gasUsed': '21000',
                'gasPrice': '50000000000',
                'isError': '1',  # Error transaction
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_normal_transactions('0xfrom')

        # Only fee should be recorded (transfer is skipped due to error)
        assert len(transactions) == 1
        assert transactions[0]['to'] == MINER


class TestGetInternalTransactions:
    """Tests for get_internal_transactions method."""

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_internal_transactions(self, mock_urlopen):
        """Test fetching internal transactions."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'hash': '0xhash1',
                'timeStamp': '1700000000',
                'from': '0xcontract',
                'to': '0xto',
                'value': '500000000000000000',  # 0.5 ETH
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_internal_transactions('0xto')

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx['tx_id'] == '0xhash1'
        assert tx['value'] == Decimal('0.5')

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_internal_transactions_blockscout(self, mock_urlopen):
        """Test internal transactions from Blockscout (uses transactionHash)."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'transactionHash': '0xhash1',  # Blockscout uses transactionHash
                'timeStamp': '1700000000',
                'from': '0xcontract',
                'to': '0xto',
                'value': '500000000000000000',
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_internal_transactions('0xto')

        assert len(transactions) == 1
        assert transactions[0]['tx_id'] == '0xhash1'


class TestGetErc20Transfers:
    """Tests for get_erc20_transfers method."""

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_erc20_transfers(self, mock_urlopen):
        """Test fetching ERC20 token transfers."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'hash': '0xhash1',
                'timeStamp': '1700000000',
                'from': '0xfrom',
                'to': '0xto',
                'value': '1000000',  # 1 USDC (6 decimals)
                'tokenSymbol': 'USDC',
                'tokenDecimal': '6',
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_erc20_transfers('0xfrom')

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx['currency'] == 'USDC'
        assert tx['value'] == Decimal('1')

    @patch('beancount_ethereum.downloader.urlopen')
    def test_get_erc20_transfers_skips_nfts(self, mock_urlopen):
        """Test that NFTs (empty tokenDecimal) are skipped."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'status': '1',
            'message': 'OK',
            'result': [{
                'hash': '0xhash1',
                'timeStamp': '1700000000',
                'from': '0xfrom',
                'to': '0xto',
                'value': '1',
                'tokenSymbol': 'NFT',
                'tokenDecimal': '',  # NFT indicator
            }]
        }).encode()
        mock_urlopen.return_value = mock_response

        api = BlockExplorerApi('https://api.etherscan.io/api', 'TEST_KEY')
        transactions = api.get_erc20_transfers('0xfrom')

        assert len(transactions) == 0


class TestDownload:
    """Tests for the download function."""

    @patch.object(BlockExplorerApi, 'get_normal_transactions')
    @patch.object(BlockExplorerApi, 'get_internal_transactions')
    @patch.object(BlockExplorerApi, 'get_erc20_transfers')
    def test_download_creates_file(
        self, mock_erc20, mock_internal, mock_normal, temp_dir
    ):
        """Test that download creates the output file."""
        mock_normal.return_value = []
        mock_internal.return_value = []
        mock_erc20.return_value = []

        config = {
            'name': 'test',
            'account_map': {'0xaddress': 'Assets:Eth'},
            'block_explorer_api_url': 'https://api.etherscan.io/api',
            'block_explorer_api_key': 'TEST_KEY',
        }

        download(config, temp_dir)

        output_file = os.path.join(temp_dir, 'test.json')
        assert os.path.exists(output_file)

        with open(output_file) as f:
            data = json.load(f)
        assert data == []

    @patch.object(BlockExplorerApi, 'get_normal_transactions')
    @patch.object(BlockExplorerApi, 'get_internal_transactions')
    @patch.object(BlockExplorerApi, 'get_erc20_transfers')
    def test_download_aggregates_transactions(
        self, mock_erc20, mock_internal, mock_normal, temp_dir
    ):
        """Test that download aggregates all transaction types."""
        mock_normal.return_value = [{'tx_id': '0x1', 'type': 'normal'}]
        mock_internal.return_value = [{'tx_id': '0x2', 'type': 'internal'}]
        mock_erc20.return_value = [{'tx_id': '0x3', 'type': 'erc20'}]

        config = {
            'name': 'test',
            'account_map': {'0xaddress': 'Assets:Eth'},
            'block_explorer_api_url': 'https://api.etherscan.io/api',
            'block_explorer_api_key': 'TEST_KEY',
        }

        download(config, temp_dir)

        output_file = os.path.join(temp_dir, 'test.json')
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 3
        tx_ids = {tx['tx_id'] for tx in data}
        assert tx_ids == {'0x1', '0x2', '0x3'}

    @patch.object(BlockExplorerApi, 'get_normal_transactions')
    @patch.object(BlockExplorerApi, 'get_internal_transactions')
    @patch.object(BlockExplorerApi, 'get_erc20_transfers')
    def test_download_processes_all_addresses(
        self, mock_erc20, mock_internal, mock_normal, temp_dir
    ):
        """Test that download fetches transactions for all addresses."""
        mock_normal.return_value = []
        mock_internal.return_value = []
        mock_erc20.return_value = []

        config = {
            'name': 'test',
            'account_map': {
                '0xaddress1': 'Assets:Eth:Wallet1',
                '0xaddress2': 'Assets:Eth:Wallet2',
            },
            'block_explorer_api_url': 'https://api.etherscan.io/api',
            'block_explorer_api_key': 'TEST_KEY',
        }

        download(config, temp_dir)

        # Each method should be called for each address
        assert mock_normal.call_count == 2
        assert mock_internal.call_count == 2
        assert mock_erc20.call_count == 2


class TestConstants:
    """Tests for module constants."""

    def test_default_currency(self):
        """Test DEFAULT_CURRENCY is ETH."""
        assert DEFAULT_CURRENCY == 'ETH'

    def test_miner_address(self):
        """Test MINER address is all f's."""
        assert MINER == '0xffffffffffffffffffffffffffffffffffffffff'

    def test_wei_value(self):
        """Test WEI is 10^18."""
        assert WEI == 10 ** 18

    def test_no_transactions_messages(self):
        """Test NO_TRANSACTIONS contains expected messages."""
        assert 'No transactions found' in NO_TRANSACTIONS
        assert 'No internal transactions found' in NO_TRANSACTIONS
        assert 'No token transfers found' in NO_TRANSACTIONS
