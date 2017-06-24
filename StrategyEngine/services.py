import threading, datetime
from babaSemantics.Semantics import GROUNDED, SCEPTICALLY_PREFERRED, IDEAL
from babaSemantics.Semantics import compute_semantic_probability
import babaSemantics.BABAProgramParser as Parser
from babaApp.models import Market, TradingSettings, Trade, Portfolio, Strategy
from babaApp.databaseController import controller
from marketData import services as market_data_service
from babaApp.extras import converters
from StrategyEngine import tradeExecutions, portfolioManagement

RECALCULATION_INTERVAL = 60  # Once a minute

BUY = 'BUY'
SELL = 'SELL'


class ModuleElements:
    pass


__m = ModuleElements()
__m.strategy_task = None
__m.task_is_running = False

__m.grounded_probabilities = {}
__m.sceptically_preferred_probabilities = {}
__m.ideal_probabilities = {}


def start_strategy_task():
    if not __m.task_is_running:
        execute_strategy_task()


def stop_strategy_task():
    if __m.task_is_running:
        __m.strategy_task.cancel()
        __m.task_is_running = False


# Updates the semantic probabilities of BUY and SELL sentences in all frameworks
def execute_strategy_task():
    user = controller.get_user()

    update_semantic_probabilities()
    perform_open_position_trades(user)
    perform_close_position_trades(user)

    __m.strategy_task = threading.Timer(RECALCULATION_INTERVAL, execute_strategy_task)
    __m.strategy_task.start()
    __m.task_is_running = True


# Iterates through strategies and recalculates the semantic probabilities
def update_semantic_probabilities():
    strategies = Strategy.objects.all()
    for strategy in strategies:
        username = strategy.user.username
        strategy_name = strategy.strategy_name

        strategy_framework = controller.get_strategy_framework(strategy, datetime.datetime.now())
        baba = Parser.BABAProgramParser(string=strategy_framework).parse()

        g_probabilities = compute_semantic_probability(GROUNDED, baba)
        s_probabilities = compute_semantic_probability(SCEPTICALLY_PREFERRED, baba)
        i_probabilities = compute_semantic_probability(IDEAL, baba)

        store_probability_tuples = [(__m.grounded_probabilities, g_probabilities),
                                    (__m.sceptically_preferred_probabilities, s_probabilities),
                                    (__m.ideal_probabilities, i_probabilities)]

        for (store, probabilities) in store_probability_tuples:
            store[username + '_' + strategy_name + '_' + BUY] = \
                probabilities[BUY] if BUY in probabilities.keys() else 0
            store[username + '_' + strategy_name + '_' + SELL] = \
                probabilities[SELL] if SELL in probabilities.keys() else 0


# Analyses semantic probabilities, cross referencing with
#  user thresholds and executes trades as required.
def perform_open_position_trades(user):
    strategies = Strategy.objects.filter(user=user)
    for strategy in strategies:
        try:
            user_trading_settings = TradingSettings.objects.get(user=user, strategy=strategy)
            if not user_trading_settings.enable_trading:
                continue

            for direction in [BUY, SELL]:
                if user_already_holds_position(user, strategy, direction):
                    continue

                key_root = get_user_strategy_key_root(strategy)
                key = key_root + direction

                if strategy_has_conflicting_recommendation(strategy, user_trading_settings.required_trade_confidence):
                    continue

                if key in __m.sceptically_preferred_probabilities.keys() and \
                        __m.sceptically_preferred_probabilities[key] >= (user_trading_settings.required_trade_confidence / 100):
                    execute_open_position(user, strategy, direction, user_trading_settings)

        except TradingSettings.DoesNotExist:
            continue


# Analyses open positions and closes them if required
# A position is closed when any of three conditions are met:
#   1) The required yield has been achieved
#   2) The loss limit has been exceeded
#   3) The strategy recommends taking an opposite position
def perform_close_position_trades(user):
    open_positions = Trade.objects.filter(portfolio__user=user, open_position=True)
    for open_position in open_positions:
        trading_settings = TradingSettings.objects.get(user=user, strategy=open_position.strategy)
        position_direction = converters.trade_type_integer_to_string(open_position.direction)

        initial_value = open_position.price * open_position.quantity

        # Distinction between bid and ask prices: if position direction == BUY: use bid price
        latest_tick = market_data_service.get_latest_tick(open_position.instrument_symbol)
        current_value_per_unit = latest_tick.bid_price if position_direction == BUY else latest_tick.ask_price
        current_value = current_value_per_unit * open_position.quantity

        if strategy_recommends_opposite_position(open_position.strategy, open_position.direction, trading_settings.required_trade_confidence):
            execute_close_position(open_position)

        # yield threshold reached
        try:
            if ((current_value - initial_value) / initial_value * 100 * open_position.direction) >= trading_settings.close_position_yield:
                execute_close_position(open_position)

            # loss limit reached
            elif ((initial_value - current_value) / initial_value * 100 * open_position.direction) >= trading_settings.close_position_loss_limit:
                execute_close_position(open_position)
        except ZeroDivisionError:
            continue


def user_already_holds_position(user, strategy, direction):
    direction_integer = converters.trade_type_string_to_integer(direction)
    existing_positions = Trade.objects.filter(portfolio__user=user,
                                              strategy=strategy,
                                              open_position=True,
                                              direction=direction_integer)

    return len(existing_positions) > 0


# A strategy has conflicting recommendations when semantic probabilities for
# both BUY and SELL are above the user specified required confidence level
# key = string, required_confidence_level = int (0-100)
def strategy_has_conflicting_recommendation(strategy, required_confidence_level):
    confidence_decimal = required_confidence_level / 100
    buy_probability = get_probability(strategy.user.username, strategy.strategy_name, 'BUY', SCEPTICALLY_PREFERRED)
    sell_probability = get_probability(strategy.user.username, strategy.strategy_name, 'SELL', SCEPTICALLY_PREFERRED)

    return buy_probability >= confidence_decimal and sell_probability > confidence_decimal


# Returns whether the strategy recommends holding the opposite position.
# (i.e. Recommends SELL position when user holds a corresponding BUY position)
def strategy_recommends_opposite_position(strategy, inspected_position_direction, required_trade_confidence):
    required_confidence_decimal = required_trade_confidence / 100

    opposite_probability = 0
    if inspected_position_direction == converters.trade_type_string_to_integer('BUY'):
        opposite_probability = get_probability(strategy.user.username, strategy.strategy_name, 'SELL', SCEPTICALLY_PREFERRED)
    if inspected_position_direction == converters.trade_type_string_to_integer('SELL'):
        opposite_probability = get_probability(strategy.user.username, strategy.strategy_name, 'BUY', SCEPTICALLY_PREFERRED)

    return opposite_probability > required_confidence_decimal


# Opens a new position, updates data stores.
# user, framework, trading_settings = database object, direction = String
def execute_open_position(user, strategy, direction, trading_settings):
    latest_price = market_data_service.get_latest_tick(strategy.market.symbol)
    quantity = trading_settings.buy_quantity if direction == BUY else trading_settings.sell_quantity
    price_per_unit = latest_price.ask_price if direction == BUY else latest_price.bid_price

    if not portfolioManagement.can_execute_trade(user, strategy, quantity, direction, price_per_unit): return

    try:
        portfolio = Portfolio.objects.get(user=user)
        trade = Trade(
            portfolio=portfolio,
            strategy=strategy,
            instrument_symbol=strategy.market.symbol,
            quantity=quantity,
            direction=converters.trade_type_string_to_integer(direction),
            price=price_per_unit,
            open_position=True,
            position_opened=datetime.datetime.now(),
            framework_at_open=strategy.framework
        )
        trade.save()

        tradeExecutions.execute_trade(strategy.strategy_name,
                                      strategy.market.symbol,
                                      quantity,
                                      direction,
                                      price_per_unit,
                                      'OPEN',
                                      trade.position_opened)

    except Portfolio.DoesNotExist:
        print('Cannot find user portfolio when creating Trade object')
    except RuntimeError:
        print('Runtime Error when creating Trade object')
        pass


def execute_close_position(open_position):
    latest_datatick = market_data_service.get_latest_tick(open_position.instrument_symbol)

    open_position.close_price = latest_datatick.bid_price \
        if converters.trade_type_integer_to_string(open_position.direction) == 'BUY' else latest_datatick.ask_price
    open_position.position_closed = datetime.datetime.now()
    open_position.open_position = False
    open_position.framework_at_close = open_position.strategy.framework
    open_position.save()

    tradeExecutions.execute_trade(open_position.strategy.strategy_name,
                                  open_position.strategy.market.symbol,
                                  open_position.quantity,
                                  converters.trade_type_integer_to_string(open_position.direction),
                                  open_position.close_price,
                                  'CLOSE',
                                  open_position.position_closed)


# Returns the probability for the corresponding framework, direction (string) and semantics
def get_probability(username, strategy_name, direction, semantics):
    key = username + '_' + strategy_name + '_' + direction

    if semantics == GROUNDED and key in __m.grounded_probabilities.keys():
        return __m.grounded_probabilities[key]
    elif semantics == SCEPTICALLY_PREFERRED and key in __m.sceptically_preferred_probabilities.keys():
        return __m.sceptically_preferred_probabilities[key]
    elif semantics == IDEAL and key in __m.ideal_probabilities.keys():
        return __m.ideal_probabilities[key]
    else:
        return 0


def get_user_strategy_key_root(strategy):
    return strategy.user.username + '_' + strategy.strategy_name + '_'


def close_positions_for_strategy(username_string, strategy_name_string):
    open_positions = Trade.objects.filter(portfolio__user__username=username_string,
                                          strategy__strategy_name=strategy_name_string)

    for position in open_positions:
        execute_close_position(position)
