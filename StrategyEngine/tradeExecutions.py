
def execute_trade(strategy_name, instrument_symbol, quantity, direction, price, open_close, datetime):
    with open('trade_executions.txt', 'a') as trade_log:

        trade = '\nExecuted order: ' + instrument_symbol + ' (' + open_close + ')' +\
                ' (quantity = ' + str(quantity) + ') ' + '@' + str(price) + ', ' +\
                direction + ' (strategy = ' + strategy_name + '), ' + str(datetime)

        trade_log.write(trade)
