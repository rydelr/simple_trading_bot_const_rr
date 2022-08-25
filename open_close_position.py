import time
from datetime import datetime

from binance.exceptions import BinanceAPIException


def close_position(client, live_position_side, pair, position_amount):
    if live_position_side == "LONG":
        side = "SELL"
    elif live_position_side == "SHORT":
        side = "BUY"
    else:
        side = "NONE"

    event_time = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')

    try:
        close_position = client.futures_create_order(symbol=pair,
                                                     side=side,
                                                     type="MARKET",
                                                     quantity=position_amount,
                                                     reduceOnly='true')
    except BinanceAPIException as e:
        if e.message == "ReduceOnly Order is rejected.":
            print(f"{event_time}: CLOSE POSITION ERROR: You have not any open position!")

        elif e.message == "Invalid side.":
            print(f"{event_time}: CLOSE POSITION ERROR: You have not chosen side to close position - "
                  f"probably you have not opened position!")

    else:
        print(f"{event_time}: ------------ POSITION SUCCESSFULLY CLOSED -------------")

    time.sleep(0.01)


def open_position(client, pair, position_side, position_amount, trade_permission):

    if position_side == "LONG":
        side = "BUY"
    elif position_side == "SHORT":
        side = "SELL"
    else:
        side = "NONE"

    event_time = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')

    if trade_permission:
        try:
            open_pos = client.futures_create_order(symbol=pair,
                                                   side=side,
                                                   type="MARKET",
                                                   quantity=position_amount,)
        except BinanceAPIException as e:
            print(f"{event_time}: OPEN POSITION ERROR: {e.message}")

        else:
            print(f"{event_time}: ---------- {side} MARKET POSITION OF {position_amount} SUCCESSFULLY OPENED ----------")
            return True
    else:
        print(f"{event_time}: Position not opened - permission to open position not granted")
