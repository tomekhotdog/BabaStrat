from babaApp.models import User, Market, TradingSettings, Portfolio, Trade, Strategy, Indicator, ExchangeEvent
from django.shortcuts import get_list_or_404
from marketData import services as market_data_services
from StrategyEngine import services as strategy_engine_services
from babaSemantics import BABAProgramParser as Parser, Semantics, formattingUtilities
from babaApp.extras import applicationStrings as strings, converters
from frameworkExtensions import service as framework_extensions_service

DELTA = 0.000001
FLOAT_FORMAT = "{0:.2f}"
NEW_LINE = '\n'

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


def get_market_for_strategy_name(user, strategy_name):
    return Strategy.objects.get(user=user, strategy_name=strategy_name).market


def get_strategy_index(user, strategy_name):
    # strategies = get_strategies_for_user(user)
    strategies = Strategy.objects.filter(user=user)
    counter = 1
    for s in strategies:
        if s.strategy_name == strategy_name:
            return counter
        counter += 1

    return 0


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
                         'strategy': trade.strategy.strategy_name,
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


def get_strategy_indicators(user, strategy_name):
    return Indicator.objects.all()


def get_strategy_macro_rules(user, strategy_name):
    strategy = Strategy.objects.filter(user=user, strategy_name=strategy_name)[0]
    if not strategy.framework_extension: return None

    macro_rules = strategy.framework_extension.split(NEW_LINE)
    return_rules = []
    for rule in macro_rules:
        if rule and len(rule.strip()) > 0:
            return_rules.append(rule)

    if len(return_rules) == 0: return None
    return return_rules


def get_strategy_framework(strategy, datetime):
    main_framework = strategy.framework
    additional_random_variables = framework_extensions_service.extract_external_random_variables(main_framework)
    additional_rules = framework_extensions_service.compute_framework_rules(strategy, datetime)
    return main_framework + ' \n ' + additional_random_variables + '\n' + additional_rules


def get_strategy_trades_for_interval(user, strategy_name, start_date, end_date):
    strategy = Strategy.objects.filter(user=user, strategy_name=strategy_name)[0]
    trades = Trade.objects.filter(strategy=strategy, position_opened__gte=start_date, position_opened__lte=end_date)
    trades_list = []
    for trade in trades:
        trade_detail = {
            'trade_type': 'OPEN',
            'quantity': trade.quantity,
            'direction': converters.trade_type_integer_to_string(trade.direction),
            'price': trade.price,
            'date': trade.position_opened,
            'framework': formattingUtilities.get_semantic_probabilities_html(trade.framework_at_open)
        }
        trades_list.append(trade_detail)

        if not trade.open_position:
            close_trade_detail = {
                'trade_type': 'CLOSE',
                'quantity': trade.quantity,
                'direction': converters.trade_type_integer_to_string(trade.direction),
                'price': trade.close_price,
                'date': trade.position_closed,
                'framework': formattingUtilities.get_semantic_probabilities_html(trade.framework_at_close)
            }
            trades_list.append(close_trade_detail)

    return trades_list


# Append to framework string representation with the relevant element
def add_framework_element(user, strategy_name, assumption=None, contrary=None, rv=None, rule=None):
    try:
        strategy = Strategy.objects.get(user=user, strategy_name=strategy_name)
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

        strategy.framework = (strategy.framework + strategy_extension)
        strategy.save()

    except Strategy.DoesNotExist:
        print('Framework with name ' + strategy_name + ' does not exist')
    except RuntimeError:
        print('Runtime error due to string manipulation of additional element')


# Append to framework extension with additional MacroRule
def add_framework_extension(user, strategy_name, macro_rule=None):
    try:
        strategy = Strategy.objects.get(user=user, strategy_name=strategy_name)
        strategy_extension = '\n'
        if macro_rule is not None:
            strategy_extension += macro_rule

        strategy.framework_extension = (strategy.framework_extension + strategy_extension)
        strategy.save()

    except Strategy.DoesNotExist:
        print('Framework with name ' + strategy_name + ' does not exist')
    except RuntimeError:
        print('Runtime error when adding new MacroRule')


def delete_strategy_element(user, strategy_name, element, type):
    try:
        strategy = Strategy.objects.get(user=user, strategy_name=strategy_name)
        framework_string = strategy.framework
        updated_framework_string = ''

        if type == 'm':
            extension_string = strategy.framework_extension
            updated_extension_string = ''
            for line in extension_string.split(NEW_LINE):
                if element in line:
                    continue

                updated_extension_string += line
                strategy.framework_extension = updated_extension_string
                strategy.save()
            pass

        elif type == 'u':
            rule_head = element.split(':-')[0].strip()
            rule_body = [elem.strip() for elem in element.split(':-')[1].split(',')]

            for line in framework_string.split(NEW_LINE):
                if 'myRule(' in line:
                    framework_rule_head = line.split('myRule(')[1].split(',')[0].strip()
                    if framework_rule_head == rule_head and all(elem in line for elem in rule_body):
                        continue

                updated_framework_string += line + '\n'

            strategy.framework = updated_framework_string
            strategy.save()

        else:
            element_to_delete = element
            element_identifier = None
            if type == 'a':
                element_identifier = 'myAsm('
            elif type == 'c':
                element_identifier = 'contrary('
            elif type == 'r':
                element_identifier = 'myRV('

            for line in framework_string.split(NEW_LINE):
                if element_identifier is not None and element_identifier in line:
                    line_element = line.split(element_identifier)[1].split(')')[0]
                    if line_element == element_to_delete:
                        continue

                updated_framework_string += line + '\n'

            strategy.framework = updated_framework_string
            strategy.save()

    except IndexError:
        pass


def enable_trading(username_string, strategy_name_string):
    strategy = Strategy.objects.filter(user__username=username_string, strategy_name=strategy_name_string)[0]
    trading_settings = TradingSettings.objects.get(strategy=strategy)
    trading_settings.enable_trading = True
    trading_settings.save()


def disable_trading(username_string, strategy_name_string):
    strategy = Strategy.objects.filter(user__username=username_string, strategy_name=strategy_name_string)[0]
    trading_settings = TradingSettings.objects.get(strategy=strategy)
    trading_settings.enable_trading = False
    trading_settings.save()


def close_positions(username_string, strategy_name_string):
    strategy_engine_services.close_positions_for_strategy(username_string, strategy_name_string)


def recalculate_probabilities():
    strategy_engine_services.stop_strategy_task()
    strategy_engine_services.start_strategy_task()


def get_exchange_events():
    return ExchangeEvent.objects.all()
