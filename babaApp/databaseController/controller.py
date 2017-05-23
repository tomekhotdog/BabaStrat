from babaApp.models import User, Framework, TradingSettings, Portfolio
from django.shortcuts import get_list_or_404


# Returns god user -> for testing
def get_user():
    return User.objects.all()[0]


def get_framework_list():
    return get_list_or_404(Framework)


def get_settings(user, framework_name):
    settings = TradingSettings.objects.filter(
        user=user,
        framework_name__framework_name=framework_name)

    if len(settings) == 0:
        framework = Framework.objects.get(framework_name=framework_name)
        new_settings = TradingSettings(user=user, framework_name=framework, enable_trading=True)
        new_settings.save()

    settings = TradingSettings.objects.get(
        user=user,
        framework_name__framework_name=framework_name)

    return settings


# Returns user current total equity and overall percentage change
def get_total_equity(user):
    portfolio = Portfolio.objects.get(user=user)
    start = portfolio.start_value
    current = portfolio.current_value
    decimal_change = abs(start - current) / start if current > start else abs(start - current) / start * -1.0

    return current, decimal_change * 100


# Returns a set of all current open positions
def get_open_positions(user):
    # TODO:
    return []


# Returns a summary of all closed positions
def get_executed_trades(user):
    # TODO:
    return []


# Returns performance summaries for each framework
def get_framework_performance(user):
    # TODO:
    return []