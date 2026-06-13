import json
import time
import threading
from websocket import WebSocketApp

# -----------------------------
# CONFIG
# -----------------------------
SYMBOL = "btcusdt"
DEPTH_STREAM = f"{SYMBOL}@depth@100ms"
WS_URL = f"wss://stream.binance.com:9443/ws/{DEPTH_STREAM}"

RANGE_PCT = 0.005  # 0.5%

# -----------------------------
# LOCAL ORDER BOOK STATE
# -----------------------------
bids = {}  # price -> size
asks = {}  # price -> size


# -----------------------------
# APPLY DEPTH UPDATES
# -----------------------------
def update_book(side_dict, updates):
    for price_str, size_str in updates:
        price = float(price_str)
        size = float(size_str)

        if size == 0:
            side_dict.pop(price, None)
        else:
            side_dict[price] = size


def process_message(msg):
    global bids, asks

    data = json.loads(msg)

    if "b" in data:
        update_book(bids, data["b"])

    if "a" in data:
        update_book(asks, data["a"])


# -----------------------------
# MDR CALCULATION
# -----------------------------
def calculate_mdr():
    if not bids or not asks:
        return 0, 0, 0

    best_bid = max(bids.keys())
    best_ask = min(asks.keys())
    mid = (best_bid + best_ask) / 2

    bid_vol = 0
    ask_vol = 0

    for price, size in bids.items():
        if price >= mid * (1 - RANGE_PCT):
            bid_vol += price * size

    for price, size in asks.items():
        if price <= mid * (1 + RANGE_PCT):
            ask_vol += price * size

    if bid_vol + ask_vol == 0:
        return 0, bid_vol, ask_vol

    mdr = (bid_vol - ask_vol) / (bid_vol + ask_vol) * 100
    return mdr, bid_vol, ask_vol


# -----------------------------
# WEBSOCKET CALLBACKS
# -----------------------------
def on_message(ws, message):
    process_message(message)


def on_open(ws):
    print("WebSocket connected.")


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")


# -----------------------------
# MDR PRINT LOOP
# -----------------------------
def print_loop():
    while True:
        mdr, bid_vol, ask_vol = calculate_mdr()
        print(f"MDR: {mdr:.4f} | Bids: {bid_vol:.2f} | Asks: {ask_vol:.2f}")
        time.sleep(2)


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    ws = WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close
    )

    # run printing in background thread
    thread = threading.Thread(target=print_loop, daemon=True)
    thread.start()

    ws.run_forever()