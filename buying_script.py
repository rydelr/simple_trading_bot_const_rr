import open_close_position


def open_next_position(client, pair, side, actual_price, entry_price, entry_amount, next_pos_step,
                       number_of_position, trade_permission: bool = False):
    new_position = False

    if side == "LONG":
        if actual_price > entry_price * (1 + number_of_position * next_pos_step/100):

            new_position = open_close_position.open_position(client=client,
                                                             pair=pair,
                                                             position_side=side,
                                                             position_amount=entry_amount,
                                                             trade_permission=trade_permission)

    elif side == "SHORT":
        if actual_price < entry_price * (1 - number_of_position * next_pos_step/100):

            new_position = open_close_position.open_position(client=client,
                                                             pair=pair,
                                                             position_side=side,
                                                             position_amount=entry_amount,
                                                             trade_permission=trade_permission)
    return new_position
