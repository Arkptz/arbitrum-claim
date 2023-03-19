from web3 import Web3
from web3 import Account
from web3.eth import AsyncEth
from loguru import logger as log
import traceback
import asyncio
from time import sleep, time
from abi import abi, token_abi
from config import TRANSFER_ADDRESS, NODE_ARB, NODE_ETH, MAX_GWEI_PRICE
from hexbytes.main import HexBytes
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

BINANCE_ADDRESS = CONTRACT_ADDRESS
print(TOKEN_CONTRACT.all_functions())
contract_balance_tokens = TOKEN_CONTRACT.functions.balanceOf(
    CONTRACT_ADDRESS).call()
print("Contract balance tokens:", contract_balance_tokens / DECIMAL)
claimable_amount = CONTRACT.functions.claimableTokens(ADDRESS).call()
print("Claimable amount:", claimable_amount / DECIMAL)
# Получаем время начала и окончания периода
claim_period_start = CONTRACT.functions.claimPeriodStart().call()
claim_period_end = CONTRACT.functions.claimPeriodEnd().call()
print("Claim period start:", claim_period_start)
print("Claim period end:", claim_period_end)

# Получаем текущий номер блока
current_block_number = web3_eth_no_sync.eth.block_number
print("Current block number:", current_block_number)
left_to_go = claim_period_start - current_block_number
print("Blocks left to go:", left_to_go)


class Arbitrum:
    account: Account
    private_key: str
    address: str
    amount_tokens: int

    def __init__(self, private_key: str) -> None:
        self.account = Account.from_key(private_key=private_key)
        self.private_key = private_key
        self.address = self.account.address

    async def wait_tokens(self):
        while True:
            amount = TOKEN_CONTRACT.functions.balanceOf(
                self.address).call()
            if amount > 0:
                self.amount_tokens = amount
                break
            await asyncio.sleep(5)

    def check_tokens_to_claim(self):
        

    async def claim(self):
        gas_price = await self.get_gas_price()
        transaction = CONTRACT.functions.claim().build_transaction({'chainId': await web3.eth.chain_id,
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
        log.success(f'Transaction claim complete. Hash - {readable_hash}')
        if TRANSFER_ADDRESS:
            await self.wait_tokens()
            await self.trasfer_tokens()

    async def trasfer_tokens(self):
        amount = self.amount_tokens
        gas_price = await self.get_gas_price()
        amount_d = amount // DECIMAL
        transaction = TOKEN_CONTRACT.functions.transfer(TRANSFER_ADDRESS, amount).build_transaction({'chainId': await web3.eth.chain_id,
                                                                                                     'from': self.address,
                                                                                                     'gasPrice': gas_price,
                                                                                                     'nonce': await web3.eth.get_transaction_count(self.address),
                                                                                                     'gas': 1_000_000,
                                                                                                     'value': 0})
        txn_hash = await self.send_tx(transaction)
        readable_hash = txn_hash.hex()
        log.success(
            f'Success transaction to {TRANSFER_ADDRESS} by {amount_d} ARB, tx hash - {readable_hash}')
        await self.wait_tx(txn_hash)
        log.success(f'Transaction complete. Hash - {readable_hash}')

    async def send_tx(self, tx: dict) -> HexBytes:
        signed_txn = web3.eth.account.sign_transaction(
            tx, self.private_key)

        txn_hash = await web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash

    async def wait_tx(self, hash: HexBytes):
        await web3.eth.wait_for_transaction_receipt(hash, timeout=300)

    async def get_gas_price(self):
        gas_price = await web3.eth.gas_price
        current_gas = gas_price / DECIMAL_GWEI
        if current_gas * 3 > MAX_GWEI_PRICE:
            gas_price = round(MAX_GWEI_PRICE * DECIMAL_GWEI)
        else:
            gas_price = round(gas_price * 3)
        return gas_price


arb = Arbitrum(pk)
asyncio.run(arb.trasfer_tokens())


def check_claim():
    try:
        CONTRACT.functions.claim().call({'from': ADDRESS})
        log.success('КЛЕЙМ ДОСТУПЕН!')
        return True
    except:
        exc = traceback.format_exc()
        exc = exc.split('reverted: ')[1].split('\n')[0]
        if (not 'claim not started' in exc) and (not 'claim ended' in exc):
            log.success('КЛЕЙМ ДОСТУПЕН!')
            return True
        log.error(exc)


while True:
    time_start_check = time()
    check_claim()
    log.info(f'Check_time: {time()- time_start_check}')
    sleep(5)

# # Проверяем, находится ли текущий блок внутри периода
# if claim_period_start <= current_block_number < claim_period_end:
#     print("Inside claim period")
# else:
#     print("Outside claim period")
