TRANSFER_ADDRESS = '0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9' #если не требуется никуда переводить сразу после клейма, здесь должно быть None
NODE_ARB = 'https://light-late-replica.arbitrum-mainnet.discover.quiknode.pro/bbf86cef31fc5047924324946b0184d69a15f99a/' #Ножа арбитрум
NODE_ETH = 'https://eth.llamarpc.com' #нода эфира (следим за блоками)
MAX_GWEI_PRICE = 10 #максимальная цена газа (обычно 0.1) но софт будет умножать цену газа сети на 3 и если она больше MAX_GWEI_PRICE, будет ставиться MAX_GWEI_PRICE
CHECK_TOKENS = False # Проверять есть ли токены для клейма на кошельке, False - нет, True - да
CHECK = True #автоматическая проверка доступен ли клейм, если что-то пойдёт не так (все клеймят а мы нет) нужно поставить значение False и перезапустить софт
#учитывайте цену и загоняйте побольше эфира на кошельки +- MAX_GWEI_PRICE/0.1 * 0.0001 ETH