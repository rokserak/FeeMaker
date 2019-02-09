from bitmex_websocket import BitMEXWebsocket
import bitmex
import time
from datetime import datetime
import dateutil.parser
import sys
import json

with open("api_keys.json", "r") as read_file:
    apiKljuci = json.load(read_file)

symbol = 'XBTUSD'
client = bitmex.bitmex(test=True, api_key=apiKljuci['http']['key'], api_secret=apiKljuci['http']['secret'])
ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=symbol, api_key=apiKljuci['websocket']['key'],
                     api_secret=apiKljuci['websocket']['secret'])

lastRenew = datetime.now()

while (True):  # work till ban :(

    amount = 1000  # set whatever you want
    switchCounter = 0
    offsetClose = 0
    lastPosSet = datetime.now()

    try:

        pos = client.Position.Position_get().result()[0]
        for i in pos:
            if (i['symbol'] == symbol):
                position = i
                break

        if (position['currentQty'] == 0):  # treba se zazihrat de ni nobenih open positionu
            # also ce program crasha to pumaga de se lepo zaprejo orderji

            offsetLong = 0
            offsetShort = 0

            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()  # dead man switch start
            switchCounter = 0

            kukCajta = datetime.now() - lastRenew

            if (kukCajta.seconds / 60 > 15):  # renew ws connection cause live feed lagging, renew every hour
                ws.exit()
                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=symbol,
                                     api_key=apiKljuci['websocket']['key'], api_secret=apiKljuci['websocket']['secret'])
                lastRenew = datetime.now()

            if (ws.get_instrument()['volume'] < ws.get_instrument()['volume24h'] / 24 / 0.7):  # avoid pumps/dumps
                # only trade when volume is 2/3 of average volume

                d = dateutil.parser.parse(ws.get_instrument()['fundingTimestamp'])
                d = d.replace(tzinfo=None)
                razlika = d - datetime.utcnow()
                print(razlika.seconds / 60)
                if (razlika.seconds / 60 > 30):  # check funding closing

                    result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount,
                                                     price=ws.recent_trades()[0]['price'] - offsetLong,
                                                     execInst='ParticipateDoNotInitiate').result()
                    while (True):  # check if order succesful else try again
                        if (result1[0]['ordStatus'] == 'New'):
                            print('order LONG uspesen')
                            break
                        else:
                            time.sleep(2)
                            offsetLong += 0.5
                            result1 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=amount,
                                                             price=ws.recent_trades()[0]['price'] - offsetLong,
                                                             execInst='ParticipateDoNotInitiate').result()
                            print('LONG retry')
                            if (switchCounter > 5):
                                deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                switchCounter = 0
                            else:
                                switchCounter += 1

                    result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount,
                                                     price=ws.recent_trades()[0]['price'] + offsetShort,
                                                     execInst='ParticipateDoNotInitiate').result()
                    while (True):
                        if (result2[0]['ordStatus'] == 'New'):
                            print('order SHORT uspesen')
                            break
                        else:
                            time.sleep(2)
                            offsetShort += 0.5
                            result2 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-amount,
                                                             price=ws.recent_trades()[0]['price'] + offsetShort,
                                                             execInst='ParticipateDoNotInitiate').result()
                            print('SHORT retry')
                            if (switchCounter > 5):
                                deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                switchCounter = 0
                            else:
                                switchCounter += 1

                    offsetClose = 0

                    while (True):  # check if any orders filled completelly
                        pos = client.Position.Position_get().result()[0]
                        for i in pos:
                            if (i['symbol'] == symbol):
                                position = i
                                break

                        if (position['openOrderBuyQty'] == 0 and position['openOrderSellQty'] > 0 and position[
                            'currentQty'] != 0):  # LONG position
                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                             orderQty=-position['currentQty'],
                                                             price=ws.recent_trades()[0]['price'] + offsetClose,
                                                             execInst='ParticipateDoNotInitiate').result()
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
                                            posSetTime = datetime.now() - lastPosSet

                                            kukCajta = datetime.now() - lastRenew

                                            if (
                                                    kukCajta.seconds / 60 > 15):  # renew ws connection cause live feed lagging, renew every hour
                                                ws.exit()
                                                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1",
                                                                     symbol=symbol,
                                                                     api_key=apiKljuci['websocket']['key'],
                                                                     api_secret=apiKljuci['websocket']['secret'])
                                                lastRenew = datetime.now()

                                            if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3 or
                                                    position['openOrderSellQty'] == 0 or posSetTime.seconds / 60 > 15):

                                                if (ws.get_instrument()['volume'] > ws.get_instrument()[
                                                    'volume24h'] / 24 * 2):
                                                    result3 = client.Order.Order_closePosition(symbol=symbol).result()
                                                    print("market close :(")
                                                    break

                                                lastPosSet = datetime.now()

                                                r = client.Order.Order_cancelAll(symbol=symbol).result()

                                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                 orderQty=-position['currentQty'],
                                                                                 price=ws.recent_trades()[0][
                                                                                           'price'] + offsetClose,
                                                                                 execInst='ParticipateDoNotInitiate').result()

                                                while (True):  # price goes far away :(
                                                    if (result3[0]['ordStatus'] == 'New'):
                                                        print('close position set again')
                                                        time.sleep(5)
                                                        if (switchCounter > 3):
                                                            deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                timeout=60000.0).result()
                                                            switchCounter = 0
                                                        else:
                                                            switchCounter += 1
                                                        break
                                                    else:
                                                        time.sleep(2)
                                                        offsetClose += 0.5
                                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                         orderQty=-position[
                                                                                             'currentQty'],
                                                                                         price=ws.recent_trades()[0][
                                                                                                   'price'] + offsetClose,
                                                                                         execInst='ParticipateDoNotInitiate').result()
                                                        print('retry close')
                                                        if (switchCounter > 5):
                                                            deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                timeout=60000.0).result()
                                                            switchCounter = 0
                                                        else:
                                                            switchCounter += 1

                                                        if (offsetClose > 100):  # price went in the wrong way
                                                            print("offset is weird - reset")
                                                            offsetClose = 0

                                                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                                                            result3 = client.Order.Order_new(symbol=symbol,
                                                                                             ordType='Limit',
                                                                                             orderQty=-position[
                                                                                                 'currentQty'], price=
                                                                                             ws.recent_trades()[0][
                                                                                                 'price'] - offsetClose,
                                                                                             execInst='ParticipateDoNotInitiate').result()

                                                            while (True):
                                                                if (result3[0]['ordStatus'] == 'New'):
                                                                    print('close position set again on other side')
                                                                    time.sleep(5)
                                                                    if (switchCounter > 3):
                                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                            timeout=60000.0).result()
                                                                        switchCounter = 0
                                                                    else:
                                                                        switchCounter += 1
                                                                    break
                                                                else:
                                                                    time.sleep(2)
                                                                    offsetClose += 0.5
                                                                    result3 = client.Order.Order_new(symbol=symbol,
                                                                                                     ordType='Limit',
                                                                                                     orderQty=-position[
                                                                                                         'currentQty'],
                                                                                                     price=
                                                                                                     ws.recent_trades()[
                                                                                                         0][
                                                                                                         'price'] - offsetClose,
                                                                                                     execInst='ParticipateDoNotInitiate').result()
                                                                    print('retry close')
                                                                    if (switchCounter > 5):
                                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                            timeout=60000.0).result()
                                                                        switchCounter = 0
                                                                    else:
                                                                        switchCounter += 1

                                            else:
                                                print('order set still viable')
                                                time.sleep(3)
                                                if (switchCounter > 3):
                                                    deadManSwitch = client.Order.Order_cancelAllAfter(
                                                        timeout=60000.0).result()
                                                    switchCounter = 0
                                                else:
                                                    switchCounter += 1

                                        else:  # finito
                                            print('position closed')
                                            r = client.Order.Order_cancelAll(symbol=symbol).result()
                                            print('all orders cancelled, new loop started')
                                            time.sleep(10)
                                            break
                                    break



                                else:
                                    time.sleep(2)
                                    offsetClose += 0.5
                                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                     orderQty=-position['currentQty'],
                                                                     price=ws.recent_trades()[0]['price'] + offsetClose,
                                                                     execInst='ParticipateDoNotInitiate').result()
                                    print('retry close')
                                    if (switchCounter > 5):
                                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                        switchCounter = 0
                                    else:
                                        switchCounter += 1
                            break


                        elif (position['openOrderSellQty'] == 0 and position['openOrderBuyQty'] > 0 and position[
                            'currentQty'] != 0):  # SHORT position
                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                             orderQty=-position['currentQty'],
                                                             price=ws.recent_trades()[0]['price'] - offsetClose,
                                                             execInst='ParticipateDoNotInitiate').result()
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
                                            posSetTime = datetime.now() - lastPosSet

                                            kukCajta = datetime.now() - lastRenew

                                            if (
                                                    kukCajta.seconds / 60 > 15):  # renew ws connection cause live feed lagging, renew every hour
                                                ws.exit()
                                                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1",
                                                                     symbol=symbol,
                                                                     api_key=apiKljuci['websocket']['key'],
                                                                     api_secret=apiKljuci['websocket']['secret'])
                                                lastRenew = datetime.now()

                                            if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3 or
                                                    position['openOrderBuyQty'] == 0 or posSetTime.seconds / 60 > 15):

                                                if (ws.get_instrument()['volume'] > ws.get_instrument()[
                                                    'volume24h'] / 24 * 2):
                                                    result3 = client.Order.Order_closePosition(symbol=symbol).result()
                                                    print("market close :(")
                                                    break

                                                lastPosSet = datetime.now()

                                                r = client.Order.Order_cancelAll(symbol=symbol).result()

                                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                 orderQty=-position['currentQty'],
                                                                                 price=ws.recent_trades()[0][
                                                                                           'price'] - offsetClose,
                                                                                 execInst='ParticipateDoNotInitiate').result()

                                                while (True):  # price goes far away :(
                                                    if (result3[0]['ordStatus'] == 'New'):
                                                        print('close position set again')
                                                        time.sleep(5)
                                                        if (switchCounter > 3):
                                                            deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                timeout=60000.0).result()
                                                            switchCounter = 0
                                                        else:
                                                            switchCounter += 1
                                                        break
                                                    else:
                                                        time.sleep(2)
                                                        offsetClose += 0.5
                                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                         orderQty=-position[
                                                                                             'currentQty'],
                                                                                         price=ws.recent_trades()[0][
                                                                                                   'price'] - offsetClose,
                                                                                         execInst='ParticipateDoNotInitiate').result()
                                                        print('retry close')
                                                        if (switchCounter > 5):
                                                            deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                timeout=60000.0).result()
                                                            switchCounter = 0
                                                        else:
                                                            switchCounter += 1

                                                        if (offsetClose > 100):  # shit went bad you are fucked
                                                            print("offset is weird - reset")
                                                            offsetClose = 0

                                                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                                                            result3 = client.Order.Order_new(symbol=symbol,
                                                                                             ordType='Limit',
                                                                                             orderQty=-position[
                                                                                                 'currentQty'], price=
                                                                                             ws.recent_trades()[0][
                                                                                                 'price'] + offsetClose,
                                                                                             execInst='ParticipateDoNotInitiate').result()

                                                            while (True):
                                                                if (result3[0]['ordStatus'] == 'New'):
                                                                    print('close position set again on other side')
                                                                    time.sleep(5)
                                                                    if (switchCounter > 3):
                                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                            timeout=60000.0).result()
                                                                        switchCounter = 0
                                                                    else:
                                                                        switchCounter += 1
                                                                    break
                                                                else:
                                                                    time.sleep(2)
                                                                    offsetClose += 0.5
                                                                    result3 = client.Order.Order_new(symbol=symbol,
                                                                                                     ordType='Limit',
                                                                                                     orderQty=-position[
                                                                                                         'currentQty'],
                                                                                                     price=
                                                                                                     ws.recent_trades()[
                                                                                                         0][
                                                                                                         'price'] + offsetClose,
                                                                                                     execInst='ParticipateDoNotInitiate').result()
                                                                    print('retry close')
                                                                    if (switchCounter > 5):
                                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                                            timeout=60000.0).result()
                                                                        switchCounter = 0
                                                                    else:
                                                                        switchCounter += 1


                                            else:
                                                print('order set still viable')
                                                time.sleep(3)
                                                if (switchCounter > 5):
                                                    deadManSwitch = client.Order.Order_cancelAllAfter(
                                                        timeout=60000.0).result()
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
                                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                     orderQty=-position['currentQty'],
                                                                     price=ws.recent_trades()[0]['price'] - offsetClose,
                                                                     execInst='ParticipateDoNotInitiate').result()
                                    print('retry close')
                                    if (switchCounter > 5):
                                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                        switchCounter = 0
                                    else:
                                        switchCounter += 1
                            break

                        elif (position['openOrderSellQty'] == 0 and position[
                            'openOrderBuyQty'] == 0):  # sam c se oba orderja naenkt zafilata CELA
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

            else:  # to j d ne trajda c je prevelk VOLUME(pump/dump)
                print('too much volume wait 30 secs')
                time.sleep(30)
                deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()

        elif (position['currentQty'] > 0):  # ce kak LONG position odprt pol ga najprej zapri
            r = client.Order.Order_cancelAll(symbol=symbol).result()

            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'],
                                             price=ws.recent_trades()[0]['price'] + offsetClose,
                                             execInst='ParticipateDoNotInitiate').result()
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
                            posSetTime = datetime.now() - lastPosSet

                            kukCajta = datetime.now() - lastRenew

                            if (
                                    kukCajta.seconds / 60 > 15):  # renew ws connection cause live feed lagging, renew every hour
                                ws.exit()
                                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=symbol,
                                                     api_key=apiKljuci['websocket']['key'],
                                                     api_secret=apiKljuci['websocket']['secret'])
                                lastRenew = datetime.now()

                            if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3 or position[
                                'openOrderSellQty'] == 0 or posSetTime.seconds / 60 > 15):

                                if (ws.get_instrument()['volume'] > ws.get_instrument()['volume24h'] / 24 * 2):
                                    result3 = client.Order.Order_closePosition(symbol=symbol).result()
                                    print("market close :(")
                                    break

                                lastPosSet = datetime.now()

                                r = client.Order.Order_cancelAll(symbol=symbol).result()

                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                 orderQty=-position['currentQty'],
                                                                 price=ws.recent_trades()[0]['price'] + offsetClose,
                                                                 execInst='ParticipateDoNotInitiate').result()

                                while (True):  # price goes far away :(
                                    if (result3[0]['ordStatus'] == 'New'):
                                        print('close position set again')
                                        time.sleep(5)
                                        if (switchCounter > 3):
                                            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                            switchCounter = 0
                                        else:
                                            switchCounter += 1
                                        break
                                    else:
                                        time.sleep(2)
                                        offsetClose += 0.5
                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                         orderQty=-position['currentQty'],
                                                                         price=ws.recent_trades()[0][
                                                                                   'price'] + offsetClose,
                                                                         execInst='ParticipateDoNotInitiate').result()
                                        print('retry close')
                                        if (switchCounter > 5):
                                            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                            switchCounter = 0
                                        else:
                                            switchCounter += 1

                                        if (offsetClose > 100):  # price went in the wrong way
                                            print("offset is weird - reset")
                                            offsetClose = 0

                                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                             orderQty=-position['currentQty'],
                                                                             price=ws.recent_trades()[0][
                                                                                       'price'] - offsetClose,
                                                                             execInst='ParticipateDoNotInitiate').result()

                                            while (True):
                                                if (result3[0]['ordStatus'] == 'New'):
                                                    print('close position set again on other side')
                                                    time.sleep(5)
                                                    if (switchCounter > 3):
                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                            timeout=60000.0).result()
                                                        switchCounter = 0
                                                    else:
                                                        switchCounter += 1
                                                    break
                                                else:
                                                    time.sleep(2)
                                                    offsetClose += 0.5
                                                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                     orderQty=-position['currentQty'],
                                                                                     price=ws.recent_trades()[0][
                                                                                               'price'] - offsetClose,
                                                                                     execInst='ParticipateDoNotInitiate').result()
                                                    print('retry close')
                                                    if (switchCounter > 5):
                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                            timeout=60000.0).result()
                                                        switchCounter = 0
                                                    else:
                                                        switchCounter += 1

                            else:
                                print('order set still viable')
                                time.sleep(3)
                                if (switchCounter > 3):
                                    deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                    switchCounter = 0
                                else:
                                    switchCounter += 1

                        else:  # finito
                            print('position closed')
                            r = client.Order.Order_cancelAll(symbol=symbol).result()
                            print('all orders cancelled, new loop started')
                            time.sleep(10)
                            break
                    break



                else:
                    time.sleep(2)
                    offsetClose += 0.5
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'],
                                                     price=ws.recent_trades()[0]['price'] + offsetClose,
                                                     execInst='ParticipateDoNotInitiate').result()
                    print('retry close')
                    if (switchCounter > 5):
                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                        switchCounter = 0
                    else:
                        switchCounter += 1


        elif (position['currentQty'] < 0):  # ce kak SHORT position odprt pol ga najprej zapri
            r = client.Order.Order_cancelAll(symbol=symbol).result()

            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'],
                                             price=ws.recent_trades()[0]['price'] - offsetClose,
                                             execInst='ParticipateDoNotInitiate').result()
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
                            posSetTime = datetime.now() - lastPosSet

                            kukCajta = datetime.now() - lastRenew

                            if (
                                    kukCajta.seconds / 60 > 15):  # renew ws connection cause live feed lagging, renew every hour
                                ws.exit()
                                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=symbol,
                                                     api_key=apiKljuci['websocket']['key'],
                                                     api_secret=apiKljuci['websocket']['secret'])
                                lastRenew = datetime.now()

                            if (abs(ws.recent_trades()[0]['price'] - result3[0]['price']) > 3 or position[
                                'openOrderBuyQty'] == 0 or posSetTime.seconds / 60 > 15):

                                if (ws.get_instrument()['volume'] > ws.get_instrument()['volume24h'] / 24 * 2):
                                    result3 = client.Order.Order_closePosition(symbol=symbol).result()
                                    print("market close :(")
                                    break

                                lastPosSet = datetime.now()

                                r = client.Order.Order_cancelAll(symbol=symbol).result()

                                result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                 orderQty=-position['currentQty'],
                                                                 price=ws.recent_trades()[0]['price'] - offsetClose,
                                                                 execInst='ParticipateDoNotInitiate').result()

                                while (True):  # price goes far away :(
                                    if (result3[0]['ordStatus'] == 'New'):
                                        print('close position set again')
                                        time.sleep(5)
                                        if (switchCounter > 3):
                                            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                            switchCounter = 0
                                        else:
                                            switchCounter += 1
                                        break
                                    else:
                                        time.sleep(2)
                                        offsetClose += 0.5
                                        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                         orderQty=-position['currentQty'],
                                                                         price=ws.recent_trades()[0][
                                                                                   'price'] - offsetClose,
                                                                         execInst='ParticipateDoNotInitiate').result()
                                        print('retry close')
                                        if (switchCounter > 5):
                                            deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                                            switchCounter = 0
                                        else:
                                            switchCounter += 1

                                        if (offsetClose > 100):  # shit went bad you are fucked
                                            print("offset is weird - reset")
                                            offsetClose = 0

                                            r = client.Order.Order_cancelAll(symbol=symbol).result()

                                            result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                             orderQty=-position['currentQty'],
                                                                             price=ws.recent_trades()[0][
                                                                                       'price'] + offsetClose,
                                                                             execInst='ParticipateDoNotInitiate').result()

                                            while (True):
                                                if (result3[0]['ordStatus'] == 'New'):
                                                    print('close position set again on other side')
                                                    time.sleep(5)
                                                    if (switchCounter > 3):
                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                            timeout=60000.0).result()
                                                        switchCounter = 0
                                                    else:
                                                        switchCounter += 1
                                                    break
                                                else:
                                                    time.sleep(2)
                                                    offsetClose += 0.5
                                                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit',
                                                                                     orderQty=-position['currentQty'],
                                                                                     price=ws.recent_trades()[0][
                                                                                               'price'] + offsetClose,
                                                                                     execInst='ParticipateDoNotInitiate').result()
                                                    print('retry close')
                                                    if (switchCounter > 5):
                                                        deadManSwitch = client.Order.Order_cancelAllAfter(
                                                            timeout=60000.0).result()
                                                        switchCounter = 0
                                                    else:
                                                        switchCounter += 1


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
                    result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['currentQty'],
                                                     price=ws.recent_trades()[0]['price'] - offsetClose,
                                                     execInst='ParticipateDoNotInitiate').result()
                    print('retry close')
                    if (switchCounter > 5):
                        deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()
                        switchCounter = 0
                    else:
                        switchCounter += 1


    except:
        print("error si fasu!!!")
        print(sys.exc_info())
        time.sleep(5)
        client = bitmex.bitmex(test=True, api_key=apiKljuci['http']['key'], api_secret=apiKljuci['http']['secret'])
        ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=symbol,
                             api_key=apiKljuci['websocket']['key'], api_secret=apiKljuci['websocket']['secret'])
