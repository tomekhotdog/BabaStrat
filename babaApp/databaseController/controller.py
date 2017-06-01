from babaApp.models import User, Market, TradingSettings, Portfolio, Trade, Strategy
from django.shortcuts import get_list_or_404
from marketData import services as market_data_services
from babaSemantics import BABAProgramParser as Parser
from babaSemantics import Semantics as Semantics
from babaApp.extras import applicationStrings as strings

DELTA = 0.000001
FLOAT_FORMAT = "{0:.2f}"


# Returns god user -> for testing
def get_user():
    return User.objects.all()[0]


def get_market_list():
    return get_list_or_404(Market)


def get_first_strategy_for_market(user, market_name):
    strategies = Strategy.objects.filter(
        user=user,
        market__market_name=market_name
    )

    if len(strategies) == 0:
        market = Market.objects.get(market_name=market_name)
        strategy_name = strings.default_strategy_name(market_name)
        new_strategy = Strategy(user=user, market=market, strategy_name=strategy_name)
        new_strategy.save()

    strategies = Strategy.objects.filter(
        user=user,
        market__market_name=market_name
    )

    return strategies[0]


def create_new_strategy(user, market_name, strategy_name):
    market = Market.objects.get(market_name=market_name)
    new_strategy = Strategy(user=user, market=market, strategy_name=strategy_name)
    new_strategy.save()


def get_settings(user, strategy_name):
    settings = TradingSettings.objects.filter(
        user=user,
        strategy__strategy_name=strategy_name)

    if len(settings) == 0:
        strategy = Strategy.objects.get(strategy_name=strategy_name)
        new_settings = TradingSettings(user=user, strategy=strategy, enable_trading=True)
        new_settings.save()

    settings = TradingSettings.objects.get(
        user=user,
        strategy__strategy_name=strategy_name)

    return settings


def get_strategies_for_user(user):
    return Strategy.objects.filter(user=user).order_by('market')


def get_strategies_for_user_and_market(user, market):
    return Strategy.objects.filter(user=user, market=market).order_by('strategy_name')


# Returns user current total equity and overall percentage change
def get_total_equity(user):  # TODO: plus value of open_positions
    portfolio = Portfolio.objects.get(user=user)
    start = portfolio.start_value
    current = portfolio.current_value
    decimal_change = abs(start - current) / start if current > start else abs(start - current) / start * -1.0

    return FLOAT_FORMAT.format(current), FLOAT_FORMAT.format(decimal_change * 100)


# Returns a list of dictionaries of all current open positions
def get_open_positions(user, market=None):
    open_trades = Trade.objects.filter(open_position=True, portfolio__user=user)
    open_trades = open_trades.filter(strategy__market=market) if market is not None else open_trades
    open_positions = []
    for trade in open_trades:
        current_price = market_data_services.get_latest_price(trade.instrument_symbol, trade.direction)
        open_position = {'symbol': trade.instrument_symbol,
                         'direction': get_direction_string(trade.direction),
                         'quantity': trade.quantity,
                         'price': trade.price,
                         'current_price': current_price,
                         'result': FLOAT_FORMAT.format(trade.direction * get_position_result(trade.price, current_price, trade.quantity)),
                         'percentage_change': FLOAT_FORMAT.format(trade.direction * get_percentage_change(trade.price, current_price))}
        open_positions.append(open_position)

    return open_positions


# Returns a (list of dictionaries) summary of all closed positions
def get_executed_trades(user):
    closed_positions = Trade.objects.filter(open_position=False, portfolio__user=user)
    executed_trades = []
    for position in closed_positions:
        trade = {'symbol': position.instrument_symbol,
                 'direction': get_direction_string(position.direction),
                 'quantity': position.quantity,
                 'price': position.price,
                 'close_price': position.close_price,
                 'result': FLOAT_FORMAT.format(position.direction * get_position_result(position.price, position.close_price, position.quantity)),
                 'percentage_change': FLOAT_FORMAT.format(position.direction * get_percentage_change(position.price, position.close_price))}
        executed_trades.append(trade)

    return executed_trades


# Returns performance summaries for each framework
def get_strategy_performance(user):
    strategies = Strategy.objects.all()
    performances = []
    for strategy in strategies:
        executed_trades = Trade.objects.filter(strategy=strategy, portfolio__user=user, open_position=False)
        invested_in_trades = sum([trade.quantity * trade.price for trade in executed_trades])
        profit = sum([((trade.close_price - trade.price) * trade.quantity * trade.direction) for trade in executed_trades])
        percentage_profit = "0.00" if (invested_in_trades < DELTA) else "{0:.2f}".format(profit / invested_in_trades * 100)
        performance = {'market_name': strategy.market.market_name,
                       'strategy_name': strategy.strategy_name,
                       'profit': FLOAT_FORMAT.format(profit),
                       'percentage_profit': percentage_profit}

        performances.append(performance)

    return performances


def get_direction_string(direction):
    if direction == 1:
        return "BUY"
    elif direction == -1:
        return "SELL"

    return "UNKNOWN" \



def get_position_result(start, end, quantity):
    return (end - start) * quantity


def get_percentage_change(start, end):
    return (end - start) / start * 100


def get_strategy_elements(user, strategy_name):
    strategy = Strategy.objects.filter(user=user, strategy_name=strategy_name)[0]
    strategy_string = strategy.framework

    baba = Parser.BABAProgramParser(string=strategy_string).parse()
    language, assumptions, contraries, rvs, rules = Semantics.string_representation(baba)

    return [language, assumptions, contraries, rvs, rules]


# Append to framework string representation with the relevant element
def extend_framework(strategy_name, assumption=None, contrary=None, rv=None, rule=None):
    try:
        strategy = Strategy.objects.get(strategy_name=strategy_name)
        strategy_extension = '\n'
        if assumption is not None:
            strategy_extension += 'myAsm(' + assumption + ').'
        if contrary is not None:
            strategy_extension += 'contrary(' + contrary + ').'
        if rv is not None:
            strategy_extension += 'myRV(' + rv + ').'
        if rule is not None:
            head = rule.split(':-')[0]
            body = rule.split(':-')[1]
            strategy_extension += 'myRule(' + head + ', [' + body + ']).'

        strategy.string_representation = (strategy.string_representation + strategy_extension)
        strategy.save()

    except Strategy.DoesNotExist:
        print('Framework with name ' + strategy_name + ' does not exist')
    except RuntimeError:
        print('Runtime error due to string manipulation of additional element')
