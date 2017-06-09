from datetime import datetime, timedelta
from babaSemantics.Semantics import GROUNDED, SCEPTICALLY_PREFERRED, IDEAL
from babaSemantics.Semantics import compute_semantic_probability
import babaSemantics.BABAProgramParser as Parser
from babaApp.models import User, TradingSettings, Trade, SimulatedTrade, Portfolio, Strategy
from marketData import queries as market_data_queries
from babaApp.extras import applicationStrings, converters
from babaApp.databaseController import controller
from marketData import queries, services

BUY = 'BUY'
SELL = 'SELL'
FLOAT_FORMAT = "{0:.4f}"


# Returns a list of labels and data points representing the back
#  test of the given user strategy over the given period
def calculate_backtest_performance(username, strategy_name, start_date, end_date):
    user = User.objects.get(username=username)
    strategy = Strategy.objects.get(strategy_name=strategy_name)

    recalculation_interval = timedelta(days=1)
    simulate_strategy_execution(user, strategy, start_date, end_date, recalculation_interval)
    labels, data_points = calculate_performance(strategy, start_date, end_date)
    clear_simulated_trades(user, strategy)

    return labels, data_points


# Simulates the given user strategy and creates the appropriate SimulatedTrade objects
# From start date, increments time by given interval, recalculates semantic probabilities
# and executes trades as required.
def simulate_strategy_execution(user, strategy, start_date, end_date, recalculation_interval):
    if start_date > end_date: return

    current_date = start_date
    while current_date <= end_date:
        try:
            calculate_semantic_probability(user, strategy, current_date, IDEAL)
            perform_open_position_trades(user, strategy, current_date)
            perform_close_position_trades(user, strategy, current_date)
        except queries.MarketDataUnavailable:
            pass

        current_date += recalculation_interval


# Calculates cumulative profit of simulated strategy over time
# (returns lists of labels and data points to plot)
def calculate_performance(strategy, start_date, end_date):
    if start_date > end_date: return [], []

    labels = []
    data_points = []
    plot_interval = 1  # Plot value one per day

    current_date = start_date
    while current_date <= end_date:
        try:
            strategy_profit = calculate_strategy_profit(strategy, current_date)

            labels.append(current_date.date())
            data_points.append(str(strategy_profit))
        except market_data_queries.MarketDataUnavailable:
            pass

        current_date += timedelta(plot_interval)

    return labels, data_points


# Calculates the cumulative profit of an executed strategy on a given date
def calculate_strategy_profit(strategy, date):
    open_positions = SimulatedTrade.objects.filter(strategy=strategy, open_position=True, position_opened__lte=date)
    closed_positions = SimulatedTrade.objects.filter(strategy=strategy, open_position=False, position_opened__lte=date)

    current_ask_price = market_data_queries.get_symbol_price(strategy.market.symbol, date, applicationStrings.BUY_DIRECTION)
    current_bid_price = market_data_queries.get_symbol_price(strategy.market.symbol, date, applicationStrings.SELL_DIRECTION)

    if current_ask_price == 0 or current_bid_price == 0: return 0  # No tick price for given date

    cumulative_profit = 0
    for position in open_positions:
        current_price = current_bid_price if position.direction == applicationStrings.BUY_DIRECTION else current_ask_price
        cumulative_profit += position.quantity * (current_price - position.price)

    for position in closed_positions:
        cumulative_profit += position.quantity * (position.close_price - position.price) * position.direction

    return cumulative_profit


# Removes all the relevant SimulatedTrade objects from the data store
def clear_simulated_trades(user, strategy):
    SimulatedTrade.objects.filter(user=user, strategy=strategy).delete()


######################################################################################################
# Strategy simulation procedures ######################################################################
######################################################################################################

class ModuleElements:
    pass


__m = ModuleElements()

__m.probabilities = {}


# Iterates through strategies and recalculates the semantic probabilities
def calculate_semantic_probability(user, strategy, date, semantics):
    strategy_framework = controller.get_strategy_framework(strategy, date)
    baba = Parser.BABAProgramParser(string=strategy_framework).parse()

    probabilities = compute_semantic_probability(semantics, baba)

    __m.probabilities[user.username + '_' + strategy.strategy_name + '_' + BUY] = probabilities[BUY] if BUY in probabilities.keys() else 0
    __m.probabilities[user.username + '_' + strategy.strategy_name + '_' + SELL] = probabilities[SELL] if SELL in probabilities.keys() else 0


# Analyses open positions and closes them if required
# A position is closed when any of three conditions are met:
#   1) The required yield has been achieved
#   2) The loss limit has been exceeded
#   3) The strategy recommends taking an opposite position
def perform_open_position_trades(user, strategy, date):
    try:
        user_trading_settings = TradingSettings.objects.get(user=user, strategy=strategy)

        # t = __m.probabilities
        key_root = get_user_strategy_key_root(strategy)
        if strategy_has_conflicting_recommendation(key_root, user_trading_settings.required_trade_confidence):
            return

        for direction in [BUY, SELL]:
            if user_already_holds_position(user, strategy, direction):
                continue

            key = key_root + direction

            if key in __m.probabilities.keys() and \
                    get_probability(user.username, strategy.strategy_name, direction) >= (user_trading_settings.required_trade_confidence / 100):
                    execute_open_position(user, strategy, direction, user_trading_settings, date)

    except TradingSettings.DoesNotExist:
        return


# Analyses open positions and closes them if required
# (with respect to the required yield or loss limit)
def perform_close_position_trades(user, strategy, date):
    open_positions = SimulatedTrade.objects.filter(user=user, open_position=True)
    for open_position in open_positions:
        trading_settings = TradingSettings.objects.get(user=user, strategy=strategy)

        if strategy_recommends_opposite_position(open_position.strategy, open_position.direction, trading_settings.required_trade_confidence):
            execute_close_position(open_position, date)

        initial_value = open_position.price * open_position.quantity
        try:
            current_price = market_data_queries.get_symbol_price(open_position.instrument_symbol, date, open_position.direction)
            current_value = current_price * open_position.quantity

            # yield threshold reached
            if ((current_value - initial_value) / initial_value * 100 * open_position.direction) >= trading_settings.close_position_yield:
                execute_close_position(open_position, date)

            # loss limit reached
            elif ((initial_value - current_value) / initial_value * 100 * open_position.direction) >= trading_settings.close_position_loss_limit:
                execute_close_position(open_position, date)

        except market_data_queries.MarketDataUnavailable:
            continue
        except ZeroDivisionError:
            continue


def user_already_holds_position(user, strategy, direction):
    direction_integer = converters.trade_type_string_to_integer(direction)
    existing_positions = SimulatedTrade.objects.filter(user=user, strategy=strategy,
                                                       open_position=True, direction=direction_integer)

    return len(existing_positions) > 0


# A strategy has conflicting recommendations when semantic probabilities for
# both BUY and SELL are above the user specified required confidence level
# key = string, required_confidence_level = int (0-100)
def strategy_has_conflicting_recommendation(key, required_confidence_level):
    confidence_decimal = required_confidence_level / 100
    buy_probability = 0
    if (key + 'BUY') in __m.probabilities.keys():
        buy_probability = __m.probabilities[key + 'BUY']
    sell_probability = 0
    if (key + 'SELL') in __m.probabilities.keys():
        sell_probability = __m.probabilities[key + 'SELL']

    return buy_probability >= confidence_decimal and sell_probability > confidence_decimal


# Returns whether the strategy recommends holding the opposite position.
# (i.e. Recommends SELL position when user holds a corresponding BUY position)
def strategy_recommends_opposite_position(strategy, inspected_position_direction, required_trade_confidence):
    required_confidence_decimal = required_trade_confidence / 100

    opposite_probability = 0
    if inspected_position_direction == converters.trade_type_string_to_integer('BUY'):
        opposite_probability = get_probability(strategy.user.username, strategy.strategy_name, 'SELL')
    if inspected_position_direction == converters.trade_type_string_to_integer('SELL'):
        opposite_probability = get_probability(strategy.user.username, strategy.strategy_name, 'BUY')

    return opposite_probability > required_confidence_decimal


# Opens a new position, updates data stores.
# user, framework, trading_settings = database object, direction = String
def execute_open_position(user, strategy, direction, trading_settings, date):
    current_price = market_data_queries.get_symbol_price(strategy.market.symbol, date, converters.trade_type_string_to_integer(direction))
    quantity = trading_settings.buy_quantity if direction == BUY else trading_settings.sell_quantity

    simulated_trade = SimulatedTrade(
        user=user,
        strategy=strategy,
        instrument_symbol=strategy.market.symbol,
        quantity=quantity,
        direction=converters.trade_type_string_to_integer(direction),
        price=current_price,
        open_position=True,
        position_opened=date
    )
    simulated_trade.save()
    log_trade_execution(strategy, direction, 'OPEN', current_price, quantity, date)


def execute_close_position(open_position, date):
    current_price = market_data_queries.get_symbol_price(open_position.instrument_symbol, date, open_position.direction)

    open_position.close_price = current_price
    open_position.position_closed = date
    open_position.open_position = False
    open_position.save()

    log_trade_execution(open_position.strategy, converters.trade_type_integer_to_string(open_position.direction),
                        'CLOSE', open_position.close_price, open_position.quantity, date)


# Returns the probability for the corresponding framework, direction (string) and semantics
def get_probability(username, strategy_name, direction):
    key = username + '_' + strategy_name + '_' + direction

    if key in __m.probabilities.keys():
        return __m.probabilities[key]
    else:
        return 0  # Raise exception?


def get_user_strategy_key_root(strategy):
    return strategy.user.username + '_' + strategy.strategy_name + '_'


###################################
# Long running simulation  ########
###################################

import json


def log_trade_execution(strategy, direction, open_close, price, quantity, date):
    with open('backtest_simulations_trade_log.txt', 'a') as file:
        execution = '(' + strategy.strategy_name + ') ' + direction + ' ' + '(' + open_close + ') ' + str(quantity) + ' @' + FLOAT_FORMAT.format(price) + ' (' + str(date) + ')'
        file.write(execution + '\n')

strategies = ['audjpy_trends',
                  'audusd_trends',
                  'xauusd_trends',
                  'xagusd_trends',
                  'usdjpy_trends',
                  'usdchf_trends',
                  'usdcad_trends',
                  'nzdusd_trends',
                  'gbpusd_trends',
                  'gbpjpy_trends',
                  'gbpchf_trends',
                  'eurusd_trends',
                  'eurjpy_trends',
                  'eurgbp_trends',
                  'eurchf_trends',
                  'chfjpy_trends',
                  'audusd_trends',
                  'audjpy_trends'
                  ]

framework = "myRule(BUY , [ Uptrend, UptrendConfidence]). \n" \
            "myRV(UptrendConfidence, 0.98). \n" \
            "myRule(SELL , [ Downtrend])."

framework_extension = "Downtrend :- 50DayEMA < 100DayEMA and Close < 100DayEMA \n" \
                      "Uptrend :- 50DayEMA > 100DayEMA and Close > 100DayEMA"

cpy = 4
cpl = 4


def modify_strategies():
    for s in strategies:
        strategy = Strategy.objects.get(strategy_name=s)
        strategy.framework = framework
        strategy.framework_extension = framework_extension
        strategy.save()

        trading_settings = TradingSettings.objects.get(strategy=strategy)
        trading_settings.close_position_yield = cpy
        trading_settings.close_position_loss_limit = cpl
        trading_settings.save()


def back_test_strategies():
    with open('backtest_simulations.txt', 'a') as file:
        days = 500
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        for s in strategies:
            strategy = Strategy.objects.get(strategy_name=s)

            file.write(s + ' simulation for ' + str(days) + ' (days)')
            labels, data_points = calculate_backtest_performance('tomasz', s, start_date, end_date)
            file.write(json.dumps(data_points) + '\n')

            latest_price = services.get_latest_price(strategy.market.symbol)
            file.write('latest price for ' + strategy.market.symbol + ': ' + str(latest_price))

            file.write('\n\n')
