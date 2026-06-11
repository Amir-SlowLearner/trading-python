import time
import requests

def get_order_book(symbol="BTCUSDT", limit=1000):
    url = "https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol, "limit": limit}
    data = requests.get(url, params=params).json()
    return data



def parse_order_book(data):
    bids = [(float(price), float(size)) for price, size in data["bids"]]
    asks = [(float(price), float(size)) for price, size in data["asks"]]
    return bids, asks



def filter_range(bids, asks, range_pct=0.005):
    best_bid = bids[0][0]
    best_ask = asks[0][0]
    mid_price = (best_bid + best_ask) / 2

    bid_filtered = [
        price * size
        for price, size in bids
        if price >= mid_price * (1 - range_pct)
    ]

    ask_filtered = [
        price * size
        for price, size in asks
        if price <= mid_price * (1 + range_pct)
    ]

    return sum(bid_filtered), sum(ask_filtered)



def calculate_mdr(bid_vol, ask_vol):
    if bid_vol + ask_vol == 0:
        return 0
    return (bid_vol - ask_vol) / (bid_vol + ask_vol) *100



while True:
    data = get_order_book()
    bids, asks = parse_order_book(data)
    bid_vol, ask_vol = filter_range(bids, asks)
    mdr = calculate_mdr(bid_vol, ask_vol)
    print(f"MDR: {mdr:.4f} | Bids: {bid_vol:.2f} | Asks: {ask_vol:.2f}")
    time.sleep(2)






#symbols = ["BTCUSDT", "ETHUSDT"]
#history.append(mdr)
#mdr_smooth = sum(history[-10:]) / len(history[-10:])


