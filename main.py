from web3 import Web3
from web3 import Account
from web3.eth import AsyncEth
from loguru import logger as log
import traceback
import os
import asyncio
from time import sleep, time
from arbirtum import Arbitrum, TOKEN_CONTRACT, CONTRACT_ADDRESS, DECIMAL, CONTRACT, web3_eth_no_sync
from config import CHECK
os.system('title Made by Arkptz')

contract_balance_tokens = TOKEN_CONTRACT.functions.balanceOf(
    CONTRACT_ADDRESS).call()
log.info(f"Contract balance tokens: {contract_balance_tokens / DECIMAL}")


wallets: list[Arbitrum] = []
with open('private_keys.txt') as file:
    data = file.read().split('\n')
    for i in data:
        if i != '':
            wallets.append(Arbitrum(i))


def check_claim():
    claim_period_start = CONTRACT.functions.claimPeriodStart().call()
    claim_period_end = CONTRACT.functions.claimPeriodEnd().call()
    log.info(f"Claim period start: {claim_period_start}")
    log.info(f"Claim period end: {claim_period_end}")
    current_block_number = web3_eth_no_sync.eth.block_number
    log.info(f"Current block number: {current_block_number}")
    left_to_go = claim_period_start - current_block_number
    log.info(f"Blocks left to go: {left_to_go}")
    try:
        CONTRACT.functions.claim().call({'from': wallets[0].address})
        log.success('Claim Accessed!')
        return True
    except:
        exc = traceback.format_exc()
        exc = exc.split('reverted: ')[1].split('\n')[0]
        if (not 'claim not started' in exc) and (not 'claim ended' in exc):
            log.success('Claim Accessed!')
            return True
        log.error(exc)
    return False


async def main():
    lst = []
    for wal in wallets:
        lst.append(wal.claim())
    await asyncio.gather(*lst)


if __name__ == '__main__':
    if CHECK:
        while not check_claim():
            sleep(1)
    asyncio.run(main())
