import websocket
import json
from datetime import datetime
from json import JSONDecodeError
import time


def prices_datastream(trade_pair: str):
    global pair
    pair = trade_pair

    price_file_saving(trade_pair=trade_pair, actual_ask_price=0, actual_bid_price=0)

    depth_socket = f"wss://fstream.binance.com/ws/{pair.lower()}@depth20@100ms"

    ws = websocket.WebSocketApp(depth_socket,
                                on_message=prices_datastream_message,
                                on_close=prices_datastream_close)

    ws.run_forever(ping_interval=20)


def prices_datastream_message(ws, message):
    data = json.loads(message)
    asks = data["a"]
    bids = data["b"]

    actual_bid_price = bids[0][0]
    actual_ask_price = asks[0][0]

    price_file_saving(trade_pair=pair,
                      actual_bid_price=actual_bid_price,
                      actual_ask_price=actual_ask_price)


def prices_datastream_close(ws):
    error_time = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
    print(f"{error_time}: ### ORDERBOOK DATA STREAM CONNECTION TERMINATED ###")
    time.sleep(10)
    prices_datastream(pair)


def price_file_saving(trade_pair, actual_bid_price, actual_ask_price):

    prices = {"actual_ask_price": actual_ask_price,
              "actual_bid_price": actual_bid_price}

    with open(f"config//actual_prices_{trade_pair}.json", 'w') as fs:
        json.dump(prices, fs, indent=4)


def actual_prices_check(trade_pair):
    while True:
        try:
            with open(f"config//actual_prices_{trade_pair}.json", 'r') as fs:
                output = json.load(fs)

        except FileNotFoundError:
            print("No file found - creating new file")
            price_file_saving(trade_pair=trade_pair, actual_ask_price=0, actual_bid_price=0)

        except JSONDecodeError:
            pass

        else:
            actual_ask_price = output["actual_ask_price"]
            actual_bid_price = output["actual_bid_price"]

            return actual_bid_price, actual_ask_price
