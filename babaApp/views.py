from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse

from babaSemantics import Semantics as Semantics
from babaApp.extras import specificStyling
from .models import Market, Strategy
from .forms import AssumptionForm, ContraryForm, RandomVariableForm, RuleForm, SettingsForm, StrategyPreferencesSelectionForm, trading_choices, trading_options, NewStrategyForm, StrategySelectionForm
from marketData.queries import get_json, DAY, WEEK, MONTH, YEAR, THREE_YEARS
from babaApp.databaseController import controller as controller
import marketData.services as market_data_service
import StrategyEngine.services as strategy_engine

POST = 'POST'
EMPTY = ''
FLOAT_FORMAT = "{0:.2f}"


#     Start strategy engine loop    #
strategy_engine.start_strategy_task()
#####################################


def index(request):
    context = {}
    return render(request, 'babaApp/index.html', context)


def frameworks_default(request):
    market_list = get_list_or_404(Market)
    market = market_list[0]
    return frameworks_with_market(request, market.market_name)


def frameworks_with_market(request, market_name):
    user = controller.get_user()
    strategy = controller.get_first_strategy_for_market(user, market_name)
    return frameworks(request, market_name, strategy.strategy_name)


def frameworks(request, market_name, strategy_name):
    if request.method == POST:
        process_form_submission(request, strategy_name)
        strategy_name = process_new_strategy_form(request, market_name, strategy_name)

    if not Market.objects.filter(market_name=market_name).exists():
        return frameworks_default(request)

    ##################################################################
    user = controller.get_user()
    market_list = controller.get_market_list()

    language, assumptions, contraries, rvs, rules = controller.get_strategy_elements(user, strategy_name)

    market = Market.objects.get(market_name=market_name)
    market_data_service.subscribe(market.symbol)

    buy_probability = strategy_engine.get_probability(user, strategy_name, 'BUY', Semantics.SCEPTICALLY_PREFERRED)
    sell_probability = strategy_engine.get_probability(user, strategy_name, 'SELL', Semantics.SCEPTICALLY_PREFERRED)

    # latest_price = market_data_service.get_latest_tick(framework.symbol)

    open_positions = controller.get_open_positions(user, market=market)
    total_equity, total_equity_percentage_change = controller.get_total_equity(user)
    ##################################################################

    assumption_form = AssumptionForm(initial={'assumption': 'assumption'})
    contrary_form = ContraryForm(initial={'contrary': 'assumption, contrary'})
    random_variable_form = RandomVariableForm(initial={'random_variable': 'random variable, probability'})
    rule_form = RuleForm
    new_strategy_form = NewStrategyForm
    strategy_selection_form = StrategySelectionForm()
    strategy_selection_form.fields['strategy_selection'].queryset = controller.get_strategies_for_user_and_market(user, market)

    context = {'markets': market_list, 'market_name': market_name, 'strategy_name': strategy_name,
               'open_positions': open_positions,
               'language': language, 'assumptions': assumptions, 'contraries': contraries,
               'random_variables': rvs, 'rules': rules,
               'assumption_form': assumption_form,
               'contrary_form': contrary_form,
               'rule_form': rule_form,
               'random_variable_form': random_variable_form,
               'new_strategy_form': new_strategy_form, 'strategy_selection_form': strategy_selection_form,
               'buy_probability': FLOAT_FORMAT.format(buy_probability),
               'sell_probability': FLOAT_FORMAT.format(sell_probability),
               'total_equity': total_equity,
               'total_equity_percentage_change': total_equity_percentage_change}

    return render(request, 'babaApp/frameworks.html', context)


def learn(request):
    market_list = get_list_or_404(Market)
    context = {'markets': market_list,
               'style': specificStyling.get_sidebar_styling('learn')}

    return render(request, 'babaApp/learn.html', context)


def settings_default(request):
    return settings(request, EMPTY)


def settings(request, selected_strategy_name):
    user = controller.get_user()
    settings_form = SettingsForm()
    strategy_selection_form = StrategyPreferencesSelectionForm()
    strategy_selection_form.fields['strategy_selection'].queryset = controller.get_strategies_for_user(user)

    if request.method == POST:
        strategy_selection_form = StrategyPreferencesSelectionForm(request.POST)

        # Framework has been selected by user
        if strategy_selection_form.is_valid():
            selected_strategy_name = strategy_selection_form.cleaned_data['strategy_selection'].strategy_name

        # Settings form submission
        if 'strategy_selection' not in request.POST:
            process_settings_form_submission(request, selected_strategy_name)

        # Settings form submission
        if not selected_strategy_name == EMPTY:
            s = controller.get_settings(controller.get_user(), selected_strategy_name)
            settings_form = SettingsForm(initial={'enable_trading': trading_choices[s.enable_trading],
                                                  'trading_options': trading_options[s.trading_options],
                                                  'buy_quantity': s.buy_quantity,
                                                  'sell_quantity': s.sell_quantity,
                                                  'required_trade_confidence': s.required_trade_confidence,
                                                  'close_position_yield': s.close_position_yield,
                                                  'close_position_loss_limit': s.close_position_loss_limit})
            strategy_selection_form = StrategyPreferencesSelectionForm(initial={'strategy_selection': selected_strategy_name})

    markets = controller.get_market_list()

    context = {'markets': markets, 'strategy_selection_form': strategy_selection_form,
               'settings_form': settings_form, 'selected_strategy': selected_strategy_name,
               "style": specificStyling.get_sidebar_styling('settings')}

    return render(request, 'babaApp/settings.html', context)


def reports(request):
    market_list = get_list_or_404(Market)

    total_equity, percentage_change = controller.get_total_equity(controller.get_user())
    open_positions = controller.get_open_positions(controller.get_user())
    executed_trades = controller.get_executed_trades(controller.get_user())
    strategy_performance = controller.get_strategy_performance(controller.get_user())
    # TODO: overall performance metrics

    context = {'markets': market_list, 'total_equity': total_equity,
               'open_positions': open_positions, 'executed_trades': executed_trades,
               'strategy_performance': strategy_performance,
               'percentage_change': percentage_change,
               "style": specificStyling.get_sidebar_styling('reports')}

    return render(request, 'babaApp/reports.html', context)


# Add new element to framework string representation (from form submission)
def process_form_submission(request, strategy_name):
    if 'assumption' in request.POST:
        form = AssumptionForm(request.POST)
        if form.is_valid():
            new_assumption = form.cleaned_data['assumption']
            controller.extend_framework(strategy_name, assumption=new_assumption)

    elif 'contrary' in request.POST:
        form = ContraryForm(request.POST)
        if form.is_valid():
            new_contrary = form.cleaned_data['contrary']
            controller.extend_framework(strategy_name, contrary=new_contrary)

    elif 'random_variable' in request.POST:
        form = RandomVariableForm(request.POST)
        if form.is_valid():
            new_rv = form.cleaned_data['random_variable']
            controller.extend_framework(strategy_name, rv=new_rv)

    elif 'rule' in request.POST:
        form = RuleForm(request.POST)
        if form.is_valid():
            new_rule = form.cleaned_data['rule']
            controller.extend_framework(strategy_name, rule=new_rule)


def process_new_strategy_form(request, market_name, strategy_name):
    user = controller.get_user()
    if 'new_strategy' in request.POST:
        form = NewStrategyForm(request.POST)
        if form.is_valid():
            new_strategy_name = form.cleaned_data['new_strategy']
            controller.create_new_strategy(user, market_name, new_strategy_name)
            return new_strategy_name

    if 'strategy_selection' in request.POST:
        form = StrategySelectionForm(request.POST)
        if form.is_valid():
            strategy_name = form.cleaned_data['strategy_selection'].strategy_name
    return strategy_name


def process_settings_form_submission(request, strategy_name):
    settings_form = SettingsForm(request.POST)
    s = controller.get_settings(controller.get_user(), strategy_name)

    s.enable_trading = True if settings_form.data['enable_trading'] == 'yes' else False
    s.trading_options = settings_form.data['trading_options']
    s.buy_quantity = settings_form.data['buy_quantity']
    s.sell_quantity = settings_form.data['sell_quantity']
    s.required_trade_confidence = settings_form.data['required_trade_confidence']
    s.close_position_yield = settings_form.data['close_position_yield']
    s.close_position_loss_limit = settings_form.data['close_position_loss_limit']
    s.save()


def chart_data(request, instrument_name, duration):
    data = get_json(instrument_name, duration)

    return JsonResponse(data)
