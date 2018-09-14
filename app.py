from bitmex_websocket import BitMEXWebsocket
import bitmex
import random, string
import math
import time

client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")
ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XRPU18", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")
symbol = 'XRPU18'

while(True): #work till ban :(
    currentPrice = ws.recent_trades()[0]['price'] #live price
    priceShort = currentPrice + 0.00000001
    priceLong = currentPrice - 0.00000001
    #amount = math.floor(ws.funds()['amount'] * 100000000 * currentPrice) #floor to round number
    amount = 500

    randID1 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #make random string for checking open orders
    randID2 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))

    offsetLong = 0.00000001
    offsetShort = 0.00000001

    result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
    while(True): #check if order succesful else try again
        if(result1[0]['ordStatus'] == 'New'):
            print('order LONG uspesen')
            break
        else:
            offsetLong += 0.00000001
            result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
            print('LONG retry')

    result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
    while (True):
        if (result2[0]['ordStatus'] == 'New'):
            print('order SHORT uspesen')
            break
        else:
            offsetShort += 0.00000001
            result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
            print('SHORT retry')

    offsetClose = 0.00000030

    randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))  # for 3rd order
    while(True): #check if any orders filled completelly
        for i in client.Position.Position_get().result()[0]:
            if(i['symbol'] == symbol):
                position = i

        if(position['openOrderBuyQty'] == 0 and position['openOrderSellQty'] > 0):
            #client.Order.Order_cancelAll()

            result3 = client.Order.Order_closePosition(symbol=symbol, price=ws.recent_trades()[0]['price'] - offsetClose).result()
            while(True):
                if(result3[0]['ordStatus'] == 'New'):
                    print('close position set')
                    break
                else:
                    offsetClose += 0.00000001
                    result3 = client.Order.Order_closePosition(symbol=symbol, price=ws.recent_trades()[0]['price'] - offsetClose).result()
                    print('retry close')
            break


        elif(position['openOrderSellQty'] == 0 and position['openOrderBuyQty'] > 0):
            #client.Order.Order_cancelAll()

            result3 = client.Order.Order_closePosition(symbol=symbol, price=ws.recent_trades()[0]['price'] + offsetClose).result()
            while (True):
                if (result3[0]['ordStatus'] == 'New'):
                    print('close position set')
                    break
                else:
                    offsetClose += 0.00000001
                    result3 = client.Order.Order_closePosition(symbol=symbol, price=ws.recent_trades()[0]['price'] + offsetClose).result()
                    print('retry close')
            break

        else:
            time.sleep(2)
            print('wait 2 secs, orders not filled yet')


    while(True):
        for i in client.Position.Position_get().result()[0]:
            if (i['symbol'] == symbol):
                position = i

        if(position['isOpen'] == False):

            r = client.Order.Order_cancelAll(symbol=symbol).result()
            print('all orders cancelled, new loop started')
            time.sleep(10)
            break
        else:
            print('order still open, wait 5 secs')
            time.sleep(5)
