
def stop_loss_check(actual_price: float, entry_price: float, stop_loss_value: float, side: str = "None"):
    if side == "LONG":
        if actual_price < (entry_price * (1 - stop_loss_value/100)):
            return True
        else:
            return False

    elif side == "SHORT":
        if actual_price > (entry_price * (1 + stop_loss_value/100)):
            return True
        else:
            return False

    else:
        print("No position side chosen to start checking stop loss.")
        return False


def take_profit_check(actual_price: float, entry_price: float, take_profit_value: float, side: str = "None"):
    if side == "LONG":
        if actual_price > (entry_price * (1 + take_profit_value / 100)):
            return True
        else:
            return False

    elif side == "SHORT":
        if actual_price < (entry_price * (1 - take_profit_value / 100)):
            return True
        else:
            return False

    else:
        print("No position side chosen to start checking take profit.")
        return False

