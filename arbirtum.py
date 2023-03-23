from web3 import Web3
from web3 import Account
from web3.eth import AsyncEth
from loguru import logger as log
import traceback
import threading
import asyncio
from time import sleep, time
from abi import abi, token_abi
from crypto import mnem_to_addr
from config import TRANSFER, NODE_ARB, NODE_ETH, MAX_GWEI_PRICE, CHECK_TOKENS, RANDOM_TRANSFER, CLAIM
from hexbytes.main import HexBytes
import random


DECIMAL = 10**18
DECIMAL_GWEI = 10 ** 9
web3_eth_no_sync = web3 = Web3(Web3.HTTPProvider(NODE_ETH))
web3_no_sync = web3 = Web3(Web3.HTTPProvider(NODE_ARB))
web3 = Web3(Web3.AsyncHTTPProvider(NODE_ARB), modules={
            "eth": (AsyncEth,)}, middlewares=[])
ADDRESS = Web3.to_checksum_address(
    '0x2950c4D3e8A45315C5D6400431B3e126dD5097E7')
CONTRACT_ADDRESS = Web3.to_checksum_address(
    '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9')
TOKEN_CONTRACT_ADDRESS = Web3.to_checksum_address(
    '0x912ce59144191c1204e64559fe8253a0e49e6548')
CONTRACT = web3_no_sync.eth.contract(CONTRACT_ADDRESS, abi=abi)
TOKEN_CONTRACT = web3_no_sync.eth.contract(
    TOKEN_CONTRACT_ADDRESS, abi=token_abi)
chainId = web3_no_sync.eth.chain_id

adresses = asyncio.Queue()
adresses_lst = []
with open('transfers.txt', 'r') as file:
    for i in file.read().split('\n'):
        adresses.put_nowait(i)
        adresses_lst.append(i)


class Arbitrum:
    account: Account
    private_key: str
    address: str
    amount_tokens: int
    have_tokens_to_claim = True

    def __init__(self, **kwargs) -> None:
        t = threading.Thread(target=self._thr_init, kwargs=kwargs)
        t.start()

    def _thr_init(self, private_key: str | None = None, seed: str | None = None):
        if seed:
            private_key = mnem_to_addr(seed)[0]
        self.account = Account.from_key(private_key=private_key)
        self.private_key = private_key
        self.address = self.account.address
        if CHECK_TOKENS:
            amount = self.check_tokens_to_claim()

            if amount == 0:
                log.error(f'Wallet {self.address} not have tokens to claim.')
                self.have_tokens_to_claim = False
            else:
                log.success(
                    f'Wallet {self.address} have {amount} ARB to claim.')

    async def wait_tokens(self):
        while True:
            amount = TOKEN_CONTRACT.functions.balanceOf(
                self.address).call()
            if amount > 0:
                self.amount_tokens = amount
                log.success(f'{amount/DECIMAL} ARB RECEIVED by {self.address}')
                break
            await asyncio.sleep(5)

    def check_tokens_to_claim(self):
        for i in range(5):
            try:
                return CONTRACT.functions.claimableTokens(self.address).call() / DECIMAL
            except:
                sleep(1)
        return 0

    async def claim(self):
        if self.have_tokens_to_claim:
            if CLAIM:
                try:
                    gas_price = await self.get_gas_price()
                    transaction = CONTRACT.functions.claim().build_transaction({'chainId': chainId,
                                                                                'from': self.address,
                                                                                'gasPrice': gas_price,
                                                                                'nonce': await web3.eth.get_transaction_count(self.address),
                                                                                'gas': 1_000_000,
                                                                                'value': 0})
                    txn_hash = await self.send_tx(transaction)
                    readable_hash = txn_hash.hex()
                    log.success(
                        f'Success claim by {self.address}, tx hash - {readable_hash}')
                    await self.wait_tx(txn_hash)
                    log.success(
                        f'Transaction claim complete. Hash - {readable_hash}')
                except:
                    log.error(f'Unfortunate claim by {self.address}')

            if TRANSFER:
                await self.trasfer_tokens()

    async def trasfer_tokens(self):
        await self.wait_tokens()
        amount = self.amount_tokens
        gas_price = await self.get_gas_price()
        amount_d = amount // DECIMAL
        if not RANDOM_TRANSFER:
            ta = await adresses.get()
        else:
            ta = random.choice(ta)
        transaction = TOKEN_CONTRACT.functions.transfer(ta, amount).build_transaction({'chainId': chainId,
                                                                                       'from': self.address,
                                                                                       'gasPrice': gas_price,
                                                                                       'nonce': await web3.eth.get_transaction_count(self.address),
                                                                                       'gas': 1_000_000,
                                                                                       'value': 0})
        txn_hash = await self.send_tx(transaction)
        readable_hash = txn_hash.hex()
        log.success(
            f'Success transaction to {ta} by {amount_d} ARB, tx hash - {readable_hash}')
        await self.wait_tx(txn_hash)
        log.success(f'Transaction complete. Hash - {readable_hash}')

    async def send_tx(self, tx: dict) -> HexBytes:
        for i in range(3):
            try:
                signed_txn = web3.eth.account.sign_transaction(
                    tx, self.private_key)

                txn_hash = await web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                return txn_hash
            except:
                log.error(f'Error when sending tx by {self.address}')

    async def wait_tx(self, hash: HexBytes, timeout:300):
        time_start = time()
        while True:
            if time() -timeout > time_start:
                raise
            receipt = web3.eth.get_transaction_receipt(hash)
            if receipt is not None:
                break
            await asyncio.sleep(5)

    async def get_gas_price(self):
        gas_price = await web3.eth.gas_price
        current_gas = gas_price / DECIMAL_GWEI
        if current_gas * 3 > MAX_GWEI_PRICE:
            gas_price = round(MAX_GWEI_PRICE * DECIMAL_GWEI)
        else:
            gas_price = round(gas_price * 3)
        return gas_price
