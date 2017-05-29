def execute_trade(instrument_symbol, quantity, direction, data_tick):
    t = instrument_symbol
    v = quantity * data_tick.ask_price
    # TODO: log trade, make fix message?
