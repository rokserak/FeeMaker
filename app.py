from bitmex_websocket import BitMEXWebsocket
import bitmex
import random, string

client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")
ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")
symbol = 'XBTUSD'

while(ws.wst.is_alive()): #work till ban :(
    currentPrice = ws.recent_trades()[0]['price'] #live price
    priceShort = currentPrice + 1
    priceLong = currentPrice - 1
    amount = ws.funds()['amount'] * 100000000 * currentPrice

    randID1 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #make random string for checking open orders
    randID2 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))

    while(ws.open_orders(randID1)): #till order succesfully placed
        result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=priceLong, execInst='ParticipateDoNotInitiate', clOrdID=randID1).result()
        priceLong -= 1

    while (ws.open_orders(randID2)):
        result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=priceShort, execInst='ParticipateDoNotInitiate', clOrdID=randID2).result()
        priceShort += 1

    while(ws.open_orders(randID1) and ws.open_orders(randID2)): #till one of orders is filled, other one will work as stop-loss
        if(ws.open_orders(randID1)['remainAmount'] == 0): #which one is filled
            randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #for 3rd order
            while (ws.open_orders(randID3)): #open 3rd order to close position
                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=priceShort, execInst='ParticipateDoNotInitiate', clOrdID=randID3).result()
                priceShort += 1
            break
        if(ws.open_orders(randID2)['remainAmount'] == 0):
            randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))
            while (ws.open_orders(randID3)):
                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=priceLong, execInst='ParticipateDoNotInitiate', clOrdID=randID3).result()
                priceLong -= 1
            break


#result = client.Order.Order_new(symbol='XBTUSD', ordType='Limit', orderQty=1000, price=5000.0, execInst='ParticipateDoNotInitiate', clOrdID="a20").result() #tko order postavt de je post-only
#ce hocis jt LONG das orderQty pozitivn, ce pa SHORT pa negativn
#print(result)

#client.Order.Order_cancelAll().result() #to j za pol ku se trade zapre

#print(ws.funds()) #to rabm de dubim kuk dnarja j na acounti

#print(ws.recent_trades()[0]) #dubim zadno ceno :)



