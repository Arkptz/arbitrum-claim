TRANSFER_ADDRESS = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9' #если не требуется никуда переводить сразу после клейма, здесь должно быть None
NODE_ARB = 'https://light-late-replica.arbitrum-mainnet.discover.quiknode.pro/bbf86cef31fc5047924324946b0184d69a15f99a/'
NODE_ETH = 'https://eth.llamarpc.com'
MAX_GWEI_PRICE = 10
CHECK = True #автоматическая проверка доступен ли клейм, если что-то пойдёт не так (все клеймят а мы нет) нужно поставить значение False и перезапустить софт
#учитывайте цену и загоняйте побольше эфира на кошельки +- MAX_GWEI_PRICE/0.1 * 0.0001 ETH