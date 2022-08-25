import json
from json import JSONDecodeError


class PositionCheck:
    def __init__(self, client, pair):
        self.client = client
        self.pair = pair

        self.position_side = None
        self.position_info = None

        self.position_checking()

        self.traded_amount = float(self.position_info[0]['positionAmt'])
        self.entry_price = round(float(self.position_info[0]['entryPrice']), 2)

        self.side_position_check()

    def position_checking(self):
        self.position_info = self.client.futures_position_information(symbol=self.pair)

    def side_position_check(self):

        if self.traded_amount > 0:
            self.position_side = "LONG"

        elif self.traded_amount < 0:
            self.position_side = "SHORT"

        elif self.traded_amount == 0:
            self.position_side = "NONE"

        else:
            self.position_side = "Error"


def position_count_save(pair, position_count):

    position_count_to_save = {"position_count": position_count}

    with open(f"config//position_count_{pair}.json", 'w') as fs:
        json.dump(position_count_to_save, fs, indent=4)


def position_count_check(pair):
    while True:
        try:
            with open(f"config/position_count_{pair}.json", 'r') as fs:
                output = json.load(fs)

        except FileNotFoundError:
            position_count_save(pair, 0)

        except JSONDecodeError:
            pass

        else:
            position_count = output["position_count"]

            return position_count


def first_position_params_save(pair, first_position_price, first_position_amount):
    first_position_params = {"first_position_price": first_position_price,
                             "first_position_amount": first_position_amount}

    with open(f"config//first_position_params_{pair}.json", 'w') as fs:
        json.dump(first_position_params, fs, indent=4)


def first_position_params_check(pair):
    while True:
        try:
            with open(f"config/first_position_params_{pair}.json", 'r') as fs:
                output = json.load(fs)

        except FileNotFoundError:
            first_position_params_save(pair, None, None)

        except JSONDecodeError:
            pass

        else:
            first_position_price = output["first_position_price"]
            first_position_amount = output["first_position_amount"]

            return first_position_price, first_position_amount
