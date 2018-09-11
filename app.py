from bitmex_websocket import BitMEXWebsocket
import bitmex


client = bitmex.bitmex(test=True, api_key="QvaIe_JS9125RjXvG4UutfKt", api_secret="YrpvIbPahQK8euaBAZUR9JKqUGhQ6x_1FldDktFhdBN5amiy")


ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key="oTBcvuJzFbqkuhHprfJlngUx", api_secret="nDsBbd5A12peVIqjgmiT46ealYn0aCcw6ziiOTHI8cLpftXs")



#result = client.Order.Order_new(symbol='XBTUSD', ordType='Limit', orderQty=1000, price=5000.0, execInst='ParticipateDoNotInitiate', clOrdID="a2").result() #tko order postavt de je post-only
#ce hocis jt LONG das orderQty pozitivn, ce pa SHORT pa negativn
#print(result)

#client.Order.Order_cancelAll().result() #to j za pol ku se trade zapre

#ws.funds() #to rabm de dubim kuk dnarja j na acounti

#print(ws.recent_trades()[0]['price']) #dubim zadno ceno :)





