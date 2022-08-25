import threading
import time
from binance import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError

import position_check
import stops
import open_close_position
import price_check
import buying_script

from private import api_keys

public_key, secret_key = api_keys.keyapi()

try:
    client = Client(public_key, secret_key)
except BinanceAPIException as e:
    print(e.message)


class Bot:
    def __init__(self, pair):
        self.client = client
        self.pair = pair.upper()
        self.is_position_live = False

        self.stop_loss_value = 1.5
        self.take_profit_value = 5.5
        self.next_pos_step = 0.1
        self.max_positions = 10

        self.min_price = 0
        self.max_price = 0

        self.actual_bid_price = 0
        self.actual_ask_price = 0

        self.live_position_side = "NONE"
        self.position_price = 0
        self.actual_price = 0
        self.position_amount = 0

    def run_scripts(self):
        #  uruchom skrypt do sprawdzania ceny bid i ask
        threading.Thread(daemon=True, target=self.actual_prices_check).start()

        #  uruchom skrypt do sprawdzania czy pozycja została zajęta
        threading.Thread(daemon=True, target=self.is_position_live_checking).start()

        #  uruchom skrypt do sprawdzania sl/tp
        while True:
            if self.actual_bid_price != 0 and self.actual_ask_price != 0:
                threading.Thread(daemon=True, target=self.stops_checking).start()
                break
            else:
                time.sleep(0.5)

        threading.Thread(daemon=True, target=self.buying_bot).start()

        print("--- BOT SUCCESSFULLY LOADED ---")

    def actual_prices_check(self):
        threading.Thread(daemon=True, target=price_check.prices_datastream, args=(self.pair,)).start()
        while True:
            self.actual_bid_price, self.actual_ask_price = price_check.actual_prices_check(self.pair)
            time.sleep(0.05)

    def is_position_live_checking(self):
        while True:
            try:
                live_position_status = position_check.PositionCheck(client=client, pair=self.pair)
            except BinanceAPIException as exc:
                print(exc.message)
            except ReadTimeout:
                pass
            except ConnectionError:
                pass
            else:
                if live_position_status.position_side == "LONG" or live_position_status.position_side == "SHORT":

                    self.position_price = float(live_position_status.entry_price)
                    self.position_amount = abs(float(live_position_status.traded_amount))

                self.live_position_side = live_position_status.position_side

            time.sleep(2)

    def stops_checking(self):
        while True:
            if self.live_position_side == "LONG":
                self.actual_price = float(self.actual_bid_price)

            elif self.live_position_side == "SHORT":
                self.actual_price = float(self.actual_ask_price)

            if self.live_position_side == "LONG" or self.live_position_side == "SHORT":

                stop_loss_status = stops.stop_loss_check(actual_price=self.actual_price,
                                                         entry_price=self.position_price,
                                                         stop_loss_value=self.stop_loss_value,
                                                         side=self.live_position_side)

                take_profit_status = stops.stop_loss_check(actual_price=self.actual_price,
                                                           entry_price=self.position_price,
                                                           stop_loss_value=self.take_profit_value,
                                                           side=self.live_position_side)

                if stop_loss_status or take_profit_status:
                    print(f"Entry Price: {self.position_price}, Amount: {self.position_amount}, "
                          f"Close Price: {self.actual_price}, SL status: {stop_loss_status}, "
                          f"TP status: {take_profit_status} , max price: {self.max_price}, "
                          f"min price: {self.min_price}")

                    #  Closing position:
                    open_close_position.close_position(client=self.client,
                                                       live_position_side=self.live_position_side,
                                                       pair=self.pair,
                                                       position_amount=self.position_amount)
                    time.sleep(1)

                time.sleep(0.05)
            else:
                time.sleep(2)

    def buying_bot(self):
        position_number = position_check.position_count_check(self.pair)

        while True:
            if self.live_position_side == "NONE":
                position_number = 0

            elif self.live_position_side == "LONG" or self.live_position_side == "SHORT":
                if position_number == 0:

                    position_check.first_position_params_save(self.pair, self.position_price, self.position_amount)

                    position_number = 1

                    print(f"POSITION NUMBER: {position_number}, SIDE: {self.live_position_side}, "
                          f"ENTRY PRICE: {self.position_price}, ENTRY AMOUNT: {self.position_amount}")

                elif position_number < self.max_positions:
                    # check and open new position in previous class:
                    first_trade_entry_price, first_trade_entry_amount = position_check.first_position_params_check(
                        self.pair)

                    next_position_check = buying_script.open_next_position(client=self.client,
                                                                           pair=self.pair,
                                                                           side=self.live_position_side,
                                                                           actual_price=self.actual_price,
                                                                           entry_price=first_trade_entry_price,
                                                                           entry_amount=first_trade_entry_amount,
                                                                           next_pos_step=self.next_pos_step,
                                                                           number_of_position=position_number,
                                                                           trade_permission=True)
                    if next_position_check:
                        position_number += 1
                        time.sleep(3)
                        print(f"POSITION NUMBER: {position_number}, SIDE: {self.live_position_side}, "
                              f"AVERAGE ENTRY PRICE: {self.position_price}, TOTAL AMOUNT: {self.position_amount}")

            position_check.position_count_save(self.pair, position_number)

            time.sleep(0.1)


bot = Bot("xmrusdt")
bot.run_scripts()

while True:
    time.sleep(10)
