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
    amount = 100

    randID1 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #make random string for checking open orders
    randID2 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))

    offsetLong = 0
    offsetShort = 0

    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result() #dead man switch start
    switchCounter = 0

    result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
    while(True): #check if order succesful else try again
        if(result1[0]['ordStatus'] == 'New'):
            print('order LONG uspesen')
            break
        else:
            offsetLong += 0.5
            result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
            print('LONG retry')

    result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
    while (True):
        if (result2[0]['ordStatus'] == 'New'):
            print('order SHORT uspesen')
            break
        else:
            offsetShort += 0.5
            result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
            print('SHORT retry')

    offsetClose = 0

    randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))  # for 3rd order
    while(True): #check if any orders filled completelly
        for i in client.Position.Position_get().result()[0]:
            if(i['symbol'] == symbol):
                position = i
                break

        if(position['openOrderBuyQty'] == 0 and position['openOrderSellQty'] > 0 and position['currentQty'] != 0):
            r = client.Order.Order_cancelAll().result()


            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
            while(True):
                if(result3[0]['ordStatus'] == 'New'):
                    print('close position set')

                    while (True):

                        for i in client.Position.Position_get().result()[0]:
                            if (i['symbol'] == symbol):
                                position = i
                                break
                        if (position['currentQty'] != 0):
                            offsetClose = 0

                            if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 5):

                                r = client.Order.Order_cancelAll().result()

                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()

                                while (True):
                                    if (result3[0]['ordStatus'] == 'New'):
                                        print('close position set again')
                                        break
                                    else:
                                        time.sleep(1)
                                        offsetClose += 0.5
                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
                                        print('retry close')
                            else:
                                print('order set still viable')
                                time.sleep(3)
                                if (switchCounter > 5):
                                    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                    switchCounter = 0
                                else:
                                    switchCounter += 1

                        else:
                            print('position closed')
                            r = client.Order.Order_cancelAll(symbol=symbol).result()
                            print('all orders cancelled, new loop started')
                            time.sleep(10)
                            break
                    break


                    break
                else:
                    time.sleep(1)
                    offsetClose += 0.5
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
                    print('retry close')
            break


        elif(position['openOrderSellQty'] == 0 and position['openOrderBuyQty'] > 0 and position['currentQty'] != 0):
            r = client.Order.Order_cancelAll().result()


            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()
            while (True):
                if (result3[0]['ordStatus'] == 'New'):
                    print('close position set')
                    while(True):

                        for i in client.Position.Position_get().result()[0]:
                            if (i['symbol'] == symbol):
                                position = i
                                break
                        if(position['currentQty'] != 0):
                            offsetClose = 0

                            if(abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 5):

                                r = client.Order.Order_cancelAll().result()

                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()

                                while (True):
                                    if (result3[0]['ordStatus'] == 'New'):
                                        print('close position set again')
                                        break
                                    else:
                                        time.sleep(1)
                                        offsetClose += 0.5
                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()
                                        print('retry close')
                            else:
                                print('order set still viable')
                                time.sleep(3)
                                if (switchCounter > 5):
                                    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                    switchCounter = 0
                                else:
                                    switchCounter += 1

                        else:
                            print('position closed')
                            r = client.Order.Order_cancelAll(symbol=symbol).result()
                            print('all orders cancelled, new loop started')
                            time.sleep(10)
                            break
                    break



                else:
                    time.sleep(1)
                    offsetClose += 0.5
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
                    print('retry close')
            break

        else:
            time.sleep(2)
            print('wait 2 secs, orders not filled yet')
            if( switchCounter > 7):
                deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                switchCounter = 0
            else:
                switchCounter += 1


    '''
    while(True):
        for i in client.Position.Position_get().result()[0]:
            if (i['symbol'] == symbol):
                position = i
                break

        if(position['isOpen'] == False):

            r = client.Order.Order_cancelAll(symbol=symbol).result()
            print('all orders cancelled, new loop started')
            time.sleep(10)
            break
        else:
            print('order still open, wait 5 secs')
            time.sleep(5)
            if (switchCounter > 3):
                deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                switchCounter = 0
            else:
                switchCounter += 1
    '''