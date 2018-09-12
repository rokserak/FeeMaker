from bitmex_websocket import BitMEXWebsocket
import bitmex
import random, string
import math
import time

client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")
ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")
symbol = 'XBTUSD'

while(True): #work till ban :(
    currentPrice = ws.recent_trades()[0]['price'] #live price
    priceShort = currentPrice + 1
    priceLong = currentPrice - 1
    #amount = math.floor(ws.funds()['amount'] * 100000000 * currentPrice) #floor to round number
    amount = 3000

    randID1 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #make random string for checking open orders
    randID2 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))

    result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - 1, execInst='ParticipateDoNotInitiate').result()
    while(True): #check if order succesful else try again
        if(result1[0]['ordStatus'] == 'New'):
            print('order LONG uspesen')
            break
        else:
            result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - 1, execInst='ParticipateDoNotInitiate').result()

    result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + 1, execInst='ParticipateDoNotInitiate').result()
    while (True):
        if (result2[0]['ordStatus'] == 'New'):
            print('order SHORT uspesen')
            break
        else:
            result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + 1, execInst='ParticipateDoNotInitiate').result()

    '''
    while(ws.open_orders(randID1)): #till order succesfully placed
        priceLong -= 1
        result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=priceLong, execInst='ParticipateDoNotInitiate').result()

        print(result1)

    while (ws.open_orders(randID2)):
        priceShort += 1
        result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=priceShort, execInst='ParticipateDoNotInitiate').result()

        print(result2)
    '''

    randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))  # for 3rd order
    while(True): #check if any orders filled completelly
        for i in client.Position.Position_get().result()[0]:
            if(i['symbol'] == symbol):
                position = i

        if(position['openOrderBuyQty'] == 0):
            cena = position['avgEntryPrice'] + 1

            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
            while(True): #new order for closing loop
                if(result3[0]['ordStatus'] == 'New'):
                    print('order 3 uspesen')
                    break
                else:
                    cena -= 1
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
            break

        elif(position['openOrderSellQty'] == 0):
            cena = position['avgEntryPrice'] - 1

            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
            #position['execQty'] is size of position so you know how much you have to close
            while (True):
                if(result3[0]['ordStatus'] == 'New'):
                    print('order 3 uspesen')
                    break
                else:
                    cena -= 1
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
            break

        else:
            time.sleep(5)
            print('wait 5 secs, orders not filled yet')

    while(True):
        for i in client.Position.Position_get().result()[0]:
            if (i['symbol'] == symbol):
                position = i
        print('to tle je prsl')
        break




    '''
    while(ws.open_orders(randID1) and ws.open_orders(randID2)): #till one of orders is filled, other one will work as stop-loss
        if(ws.open_orders(randID1)['remainAmount'] == 0): #which one is filled
            randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #for 3rd order
            while (ws.open_orders(randID3)): #open 3rd order to close position
                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=priceShort, execInst='ParticipateDoNotInitiate', clOrdID=randID3).result()
                priceShort += 1
                print(result3)
            break
        if(ws.open_orders(randID2)['remainAmount'] == 0):
            randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))
            while (ws.open_orders(randID3)):
                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=priceLong, execInst='ParticipateDoNotInitiate', clOrdID=randID3).result()
                priceLong -= 1
                print(result3)
            break
    '''

#result = client.Order.Order_new(symbol='XBTUSD', ordType='Limit', orderQty=1000, price=5000.0, execInst='ParticipateDoNotInitiate', clOrdID="a20").result() #tko order postavt de je post-only
#ce hocis jt LONG das orderQty pozitivn, ce pa SHORT pa negativn
#print(result)

#client.Order.Order_cancelAll().result() #to j za pol ku se trade zapre

#print(ws.funds()) #to rabm de dubim kuk dnarja j na acounti

#print(ws.recent_trades()[0]) #dubim zadno ceno :)



