import bitmex
from bitmex_websocket import BitMEXWebsocket

ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XRPU18", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")


client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")

#result3 = client.Order.Order_new(symbol='XRPU18', ordType='StopLimit', orderQty=-10000, price=0.00004151, stopPx=0.00004153).result()
#print(result3)
#print(ws.open_orders('asdfs')[0])
#for i in client.Position.Position_get().result()[0]:
    #print(i)


#result = client.Order.Order_closePosition(symbol='XBTUSD', price='6280').result()
#print(result)

#openOrderBuyQty je kuk mas se buy orderja za zafilat
#openOrderSellQty je kuk sam se sell orderja za zafilat
#execQty je kuk mas udprt position kuk coinu/btc

#avgCostPrice je tista cena pr kiri se j order sprozu
#avgEntryPrice isto

#a = client.Order.Order_cancelAll().result()
#print(a)

#print(client.Position.Position_get().result()[0][1])


#'ordStatus': 'Canceled' za preverajnje a j ratu order al ne


#client.Order.Order_cancelAllAfter za dead men switch



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

#result = client.Order.Order_new(symbol='XBTUSD', ordType='Limit', orderQty=1000, price=5000.0, execInst='ParticipateDoNotInitiate', clOrdID="dfasfddfdfdfdf").result() #tko order postavt de je post-only

#print(ws.market_depth()[round(len(ws.market_depth()) / 2) - 1])

#ce hocis jt LONG das orderQty pozitivn, ce pa SHORT pa negativn
#print(result)

#client.Order.Order_cancelAll().result() #to j za pol ku se trade zapre

#print(ws.funds()) #to rabm de dubim kuk dnarja j na acounti

#print(ws.recent_trades()[0]) #dubim zadno ceno :)


'''
          cena = position['avgEntryPrice'] + 1

          result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
          #position['execQty'] is size of position so you know how much you have to close
          while (True):
              if(result3[0]['ordStatus'] == 'New'):
                  print('order 3 uspesen - SHORT')
                  break
              else:
                  cena -= 1
                  result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=-position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
          break
          '''
'''
cena = position['avgEntryPrice'] - 1

result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
while(True): #new order for closing loop
    if(result3[0]['ordStatus'] == 'New'):
        print('order 3 uspesen - LONG')
        break
    else:
        cena -= 1
        result3 = client.Order.Order_new(symbol=symbol, ordType='Limit', orderQty=position['execQty'], price=cena, execInst='ParticipateDoNotInitiate').result()
break
'''

#result3 = client.Order.Order_closePosition(symbol='XBTUSD', price=ws.recent_trades()[0]['price'] + 5).result()
#print(result3)

#deadManSwitch = client.Order.Order_cancelAllAfter(timeout=60000.0).result()

for b in client.Position.Position_get().result()[0]:
    print(b)