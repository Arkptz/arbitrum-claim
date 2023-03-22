TRANSFER = False #нужно ли переводить токены
CLAIM = True #нужно ли клеймить
#кошельки для переводова закидываем в transfers.txt
RANDOM_TRANSFER = False #перечисляем на рандомный кошелек из указанных если True, если False - по списку (тогда кошельков должно быть столько же, сколько адресов с токенами)
NODE_ARB = 'https://light-late-replica.arbitrum-mainnet.discover.quiknode.pro/bbf86cef31fc5047924324946b0184d69a15f99a/' #Нода арбитрум
NODE_ETH = 'https://boldest-sleek-pond.discover.quiknode.pro/02dae3a9bff08b999a9ffcf4145485de06eefee2/' #нода эфира (следим за блоками)
MAX_GWEI_PRICE = 10 #максимальная цена газа (обычно 0.1) но софт будет умножать цену газа сети на 3 и если она больше MAX_GWEI_PRICE, будет ставиться MAX_GWEI_PRICE
CHECK_TOKENS = True # Проверять есть ли токены для клейма на кошельке, False - нет, True - да
CHECK = True #автоматическая проверка доступен ли клейм, если что-то пойдёт не так (все клеймят а мы нет) нужно поставить значение False и перезапустить софт
#учитывайте цену и загоняйте побольше эфира на кошельки +- MAX_GWEI_PRICE/0.1 * 0.0001 ETH