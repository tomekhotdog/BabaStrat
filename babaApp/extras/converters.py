def trade_type_string_to_integer(trade_type):
    if trade_type == 'SELL' or trade_type == 'sell':
        return -1
    elif trade_type == 'BUY' or trade_type == 'buy':
        return 1

    return trade_type


def trade_type_integer_to_string(trade_type):
    if trade_type == -1:
        return 'SELL'
    elif trade_type == 1:
        return 'BUY'

    return trade_type

