from datetime import datetime, timedelta
from marketData import queries as market_data_queries
from babaApp.models import Strategy, Trade, Market
from babaApp.extras import applicationStrings
from StrategyEngine import backtest, services
from babaSemantics import Semantics
from babaApp.models import User

FLOAT_FORMAT = "{0:.2f}"


def get_performance_json(username, strategy_name, start_seconds, end_seconds):
    start_date = datetime.utcfromtimestamp(start_seconds)
    end_date = datetime.utcfromtimestamp(end_seconds)

    labels, data_points = calculate_strategy_performance(username, strategy_name, start_date, end_date)
    return get_json(strategy_name + ' performance', labels, data_points)


def get_compare_performance_json(username, strategy_name, compare_strategy_name, start_seconds, end_seconds):
    start_date = datetime.utcfromtimestamp(start_seconds)
    end_date = datetime.utcfromtimestamp(end_seconds)

    labels, data_points = calculate_strategy_performance(username, strategy_name, start_date, end_date)
    _, compare_data_points = calculate_strategy_performance(username, compare_strategy_name, start_date, end_date)
    return get_json(strategy_name + ' performance', labels, data_points, additional_data=compare_data_points, additional_label=(compare_strategy_name + ' performance'))


def get_back_test_json(username, strategy_name, start_seconds, end_seconds):
    start_date = datetime.utcfromtimestamp(start_seconds)
    end_date = datetime.utcfromtimestamp(end_seconds)

    labels, data_points = backtest.calculate_backtest_performance(username, strategy_name, start_date, end_date)
    label = strategy_name + ' (backtest)'
    return get_json(label, labels, data_points)


def get_compare_back_test_json(username, strategy_name, compare_strategy_name, start_seconds, end_seconds):
    start_date = datetime.utcfromtimestamp(start_seconds)
    end_date = datetime.utcfromtimestamp(end_seconds)

    labels, data_points = backtest.calculate_backtest_performance(username, strategy_name, start_date, end_date)
    _, compare_data_points = backtest.calculate_backtest_performance(username, compare_strategy_name, start_date, end_date)
    return get_json(strategy_name + ' (backtest)', labels, data_points, additional_data=compare_data_points, additional_label=(compare_strategy_name + ' (backtest)'))


def get_semantic_probability(username, strategy_name, sentence, semantics):
    semantic_probability = 0
    if sentence == 'BUY':
        semantic_probability = services.get_probability(username, strategy_name, services.BUY, semantics)
    elif sentence == 'SELL':
        semantic_probability = services.get_probability(username, strategy_name, services.SELL, semantics)

    return {'semantic_probability': FLOAT_FORMAT.format(semantic_probability)}


def get_empty_json():
    labels = []
    chart_data = []
    datasets = [{
        'label': '',
        'fillColor': 'rgba(163,209,255,1.0)',
        'strokeColor': "rgba(220,220,220,1)",
        'pointColor': "rgba(226,118,137,1)",
        'pointStrokeColor': "#fff",
        'pointHighlightFill': "#fff",
        'pointHighlightStroke': "rgba(220,220,220,1)",
        'pointHoverBackgroundCover': "rgba(226, 118, 137, 1)",
        'pointHoverBorderColor': "rgba(226, 118, 137, 1)",
        'lineTension': 0,
        'cubicInterpolationMode': 'default',
        'data': chart_data
    }]

    return {'labels': labels, 'datasets': datasets}


def get_json(label, labels, chart_data, additional_data=None, additional_label=None):
    datasets = [{
        'label': label,
        'lineTension': 0,
        'backgroundColor': "rgba(163,209,255,0.5)",
        'color': "rgba(163,209,255,1.0)",
        'cubicInterpolationMode': 'default',
        'data': chart_data
        }
    ]

    if additional_data is not None:
        additional_dataset = {
            'label': additional_label,
            'lineTension': 0,
            'backgroundColor': "rgba(190,139,155,0.5)",
            'color': "rgba(163,209,255,1.0)",
            'cubicInterpolationMode': 'default',
            'data': additional_data
        }

        datasets.append(additional_dataset)

    return {'labels': labels,
            'datasets': datasets}


# Returns a list of labels and data points to representing strategy performance
#
# data points correspond to relative profit of a strategy.
# Calculated as: cumulative profit on closed positions up to that date
#  and expected profit for open positions (taking that day's price)
def calculate_strategy_performance(username, strategy_name, start_date, end_date):
    if start_date > end_date: return [], []
    try:
        strategy = Strategy.objects.get(user__username=username, strategy_name=strategy_name)
    except Strategy.DoesNotExist:
        return [], []

    labels = []
    data_points = []
    plot_interval = 1  # Plot value one per day

    current_date = start_date
    start_date_profit = calculate_strategy_profit(strategy, current_date)

    while current_date <= end_date:
        try:
            strategy_profit = calculate_strategy_profit(strategy, current_date)
            profit_from_start_date = strategy_profit - start_date_profit

            labels.append(current_date.date())
            data_points.append(FLOAT_FORMAT.format(profit_from_start_date))

        except market_data_queries.MarketDataUnavailable:
            pass

        current_date += timedelta(plot_interval)

    return labels, data_points


# Calculates the cumulative profit of an executed strategy on a given date
def calculate_strategy_profit(strategy, date):
    open_positions = Trade.objects.filter(strategy=strategy, open_position=True, position_opened__lte=date)
    closed_positions = Trade.objects.filter(strategy=strategy, open_position=False, position_opened__lte=date)

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
