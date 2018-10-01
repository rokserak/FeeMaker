from bitmex_websocket import BitMEXWebsocket
import bitmex
#import random, string
#import math
import time
from datetime import datetime
import dateutil.parser

client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")
ws = BitMEXWebsocket(endpoint="wss://testnet.bitmex.com/realtime", symbol="XBTUSD", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")
symbol = 'XBTUSD'

lastRenew = datetime.now()

while(True): #work till ban :(
    #currentPrice = ws.recent_trades()[0]['price'] #live price
    #priceShort = currentPrice + 1
    #priceLong = currentPrice - 1
    #amount = math.floor(ws.funds()['amount'] * 100000000 * currentPrice) #floor to round number
    amount = 10000

    #randID1 = ''.join(random.choice(string.ascii_lowercase) for i in range(15)) #make random string for checking open orders
    #randID2 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))

    offsetLong = 0
    offsetShort = 0

    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result() #dead man switch start
    switchCounter = 0

    kukCajta = datetime.now() - lastRenew

    if(kukCajta.seconds / 3600 > 1): #renew ws connection cause live feed lagging, renew every hour
        ws.exit()
        ws = BitMEXWebsocket(endpoint="wss://testnet.bitmex.com/realtime", symbol="XBTUSD", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")
        lastRenew = datetime.now()

    if(ws.get_instrument()['volume'] < ws.get_instrument()['volume24h'] / 24): #avoid pumps/dumps

        d = dateutil.parser.parse(ws.get_instrument()['fundingTimestamp'])
        d = d.replace(tzinfo=None)
        razlika = d - datetime.utcnow()
        print(razlika.seconds / 60)
        if(razlika.seconds / 60 > 5): #check funding closing

            result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
            while (True):  # check if order succesful else try again
                if (result1[0]['ordStatus'] == 'New'):
                    print('order LONG uspesen')
                    break
                else:
                    time.sleep(2)
                    offsetLong += 0.5
                    result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount, price=ws.recent_trades()[0]['price'] - offsetLong, execInst='ParticipateDoNotInitiate').result()
                    print('LONG retry')
                    if (switchCounter > 5):
                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                        switchCounter = 0
                    else:
                        switchCounter += 1

            result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
            while (True):
                if (result2[0]['ordStatus'] == 'New'):
                    print('order SHORT uspesen')
                    break
                else:
                    time.sleep(2)
                    offsetShort += 0.5
                    result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount, price=ws.recent_trades()[0]['price'] + offsetShort, execInst='ParticipateDoNotInitiate').result()
                    print('SHORT retry')
                    if (switchCounter > 5):
                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                        switchCounter = 0
                    else:
                        switchCounter += 1

            offsetClose = 0

            #randID3 = ''.join(random.choice(string.ascii_lowercase) for i in range(15))  # for 3rd order
            while (True):  # check if any orders filled completelly
                pos = client.Position.Position_get().result()[0]
                for i in pos:
                    if (i['symbol'] == symbol):
                        position = i
                        break

                if (position['openOrderBuyQty'] == 0 and position['openOrderSellQty'] > 0 and position['currentQty'] != 0):  # LONG position
                    r = client.Order.Order_cancelAll(symbol=symbol).result()

                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
                    while (True):
                        if (result3[0]['ordStatus'] == 'New'):
                            print('close position set')

                            while (True):  # sell orderja postavla cim blizi live cene
                                pos = client.Position.Position_get().result()[0]
                                for i in pos:
                                    if (i['symbol'] == symbol):
                                        position = i
                                        break
                                if (position['currentQty'] != 0):
                                    offsetClose = 0

                                    if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3):

                                        r = client.Order.Order_cancelAll(symbol=symbol).result()

                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()

                                        while (True):  #price goes far away :(
                                            if (result3[0]['ordStatus'] == 'New'):
                                                print('close position set again')
                                                time.sleep(5)
                                                break
                                            else:
                                                time.sleep(2)
                                                offsetClose += 0.5
                                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
                                                print('retry close')
                                    else:
                                        print('order set still viable')
                                        time.sleep(3)
                                        if (switchCounter > 3):
                                            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                            switchCounter = 0
                                        else:
                                            switchCounter += 1

                                else: #finito
                                    print('position closed')
                                    r = client.Order.Order_cancelAll(symbol=symbol).result()
                                    print('all orders cancelled, new loop started')
                                    time.sleep(10)
                                    break
                            break



                        else:
                            time.sleep(2)
                            offsetClose += 0.5
                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] + offsetClose, execInst='ParticipateDoNotInitiate').result()
                            print('retry close')
                    break


                elif (position['openOrderSellQty'] == 0 and position['openOrderBuyQty'] > 0 and position['currentQty'] != 0):  # SHORT position
                    r = client.Order.Order_cancelAll(symbol=symbol).result()

                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()
                    while (True):
                        if (result3[0]['ordStatus'] == 'New'):
                            print('close position set')
                            while (True):  #
                                pos = client.Position.Position_get().result()[0]
                                for i in pos:  #
                                    if (i['symbol'] == symbol):
                                        position = i
                                        break
                                if (position['currentQty'] != 0):
                                    offsetClose = 0

                                    if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3):

                                        r = client.Order.Order_cancelAll(symbol=symbol).result()

                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()

                                        while (True):  #price goes far away :(
                                            if (result3[0]['ordStatus'] == 'New'):
                                                print('close position set again')
                                                time.sleep(5)
                                                break
                                            else:
                                                time.sleep(2)
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
                            time.sleep(2)
                            offsetClose += 0.5
                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'], price=ws.recent_trades()[0]['price'] - offsetClose, execInst='ParticipateDoNotInitiate').result()
                            print('retry close')
                    break

                elif (position['openOrderSellQty'] == 0 and position['openOrderBuyQty'] == 0):  # sam c se oba orderja naenkt zafilata CELA
                    r = client.Order.Order_cancelAll(symbol=symbol).result()
                    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                    print('all filled too fast :)')
                    break

                else:
                    time.sleep(2)
                    print('wait 2 secs, orders not filled yet')
                    if (switchCounter > 5):
                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                        switchCounter = 0
                    else:
                        switchCounter += 1

        else:
            print('funding incoming')
            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
            time.sleep(300)

    else: # to j d ne trajda c je prevelk VOLUME(pump/dump)
        print('too much volume wait 30 secs')
        time.sleep(30)
        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()