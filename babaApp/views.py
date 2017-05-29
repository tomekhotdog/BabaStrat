from django.shortcuts import render, get_list_or_404
from django.http import JsonResponse

from babaSemantics import BABAProgramParser as Parser
from babaSemantics import Semantics as Semantics
from babaApp.extras import specificStyling
from .models import Framework
from .forms import AssumptionForm, ContraryForm, RandomVariableForm, RuleForm, SettingsForm, FrameworkSelectionForm, trading_choices, trading_options
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
    framework_list = get_list_or_404(Framework)
    framework = framework_list[0]
    return frameworks(request, framework)


def frameworks(request, framework_name):
    if request.method == POST:
        process_form_submission(request, framework_name)

    if not Framework.objects.filter(framework_name=framework_name).exists():
        return frameworks_default(request)

    ##################################################################
    framework_list = controller.get_framework_list()

    language, assumptions, contraries, rvs, rules = controller.get_framework_elements(framework_name)

    framework = Framework.objects.get(framework_name=framework_name)
    market_data_service.subscribe(framework.symbol)

    buy_probability = strategy_engine.get_probability(framework_name, 'BUY', Semantics.SCEPTICALLY_PREFERRED)
    sell_probability = strategy_engine.get_probability(framework_name, 'SELL', Semantics.SCEPTICALLY_PREFERRED)

    # latest_price = market_data_service.get_latest_tick(framework.symbol)

    open_positions = controller.get_open_positions(controller.get_user(), framework=framework)
    total_equity, total_equity_percentage_change = controller.get_total_equity(controller.get_user())
    ##################################################################

    assumption_form = AssumptionForm
    contrary_form = ContraryForm
    random_variable_form = RandomVariableForm
    rule_form = RuleForm

    context = {'frameworks': framework_list, 'framework_name': framework_name, 'open_positions': open_positions,
               'language': language, 'assumptions': assumptions, 'contraries': contraries,
               'random_variables': rvs, 'rules': rules,
               'assumption_form': assumption_form,
               'contrary_form': contrary_form,
               'rule_form': rule_form,
               'random_variable_form': random_variable_form,
               'buy_probability': FLOAT_FORMAT.format(buy_probability),
               'sell_probability': FLOAT_FORMAT.format(sell_probability),
               'total_equity': total_equity,
               'total_equity_percentage_change': total_equity_percentage_change}

    return render(request, 'babaApp/frameworks.html', context)


def learn(request):
    framework_list = get_list_or_404(Framework)
    context = {'frameworks': framework_list,
               'style': specificStyling.get_sidebar_styling('learn')}

    return render(request, 'babaApp/learn.html', context)


def settings_default(request):
    return settings(request, EMPTY)


def settings(request, selected_framework):
    settings_form = SettingsForm()
    framework_selection = FrameworkSelectionForm()

    if request.method == POST:
        framework_selection_form = FrameworkSelectionForm(request.POST)

        # Framework has been selected by user
        if framework_selection_form.is_valid():
            selected_framework = framework_selection_form.cleaned_data['framework_selection']
            framework_selection = FrameworkSelectionForm(initial={'framework_selection': selected_framework})

        # Settings form submission
        if 'framework_selection' not in request.POST:
            process_settings_form_submission(request, selected_framework)

        # Settings form submission
        if not selected_framework == EMPTY:
            s = controller.get_settings(controller.get_user(), selected_framework)
            settings_form = SettingsForm(initial={'enable_trading': trading_choices[s.enable_trading],
                                                  'trading_options': trading_options[s.trading_options],
                                                  'buy_quantity': s.buy_quantity,
                                                  'sell_quantity': s.sell_quantity,
                                                  'required_trade_confidence': s.required_trade_confidence,
                                                  'close_position_yield': s.close_position_yield,
                                                  'close_position_loss_limit': s.close_position_loss_limit})
            framework_selection = FrameworkSelectionForm(initial={'framework_selection': selected_framework})

    framework_list = controller.get_framework_list()

    context = {'frameworks': framework_list, 'framework_selection': framework_selection,
               'settings_form': settings_form, 'selected_framework': selected_framework,
               "style": specificStyling.get_sidebar_styling('settings')}

    return render(request, 'babaApp/settings.html', context)


def reports(request):
    framework_list = get_list_or_404(Framework)

    total_equity, percentage_change = controller.get_total_equity(controller.get_user())
    open_positions = controller.get_open_positions(controller.get_user())
    executed_trades = controller.get_executed_trades(controller.get_user())
    framework_performance = controller.get_framework_performance(controller.get_user())
    # TODO: overall performance metrics

    context = {'frameworks': framework_list, 'total_equity': total_equity,
               'open_positions': open_positions, 'executed_trades': executed_trades,
               'framework_performance': framework_performance,
               'percentage_change': percentage_change,
               "style": specificStyling.get_sidebar_styling('reports')}

    return render(request, 'babaApp/reports.html', context)


# Add new element to framework string representation (from form submission)
def process_form_submission(request, framework_name):
    if 'assumption' in request.POST:
        form = AssumptionForm(request.POST)
        if form.is_valid():
            new_assumption = form.cleaned_data['assumption']
            controller.extend_framework(framework_name, assumption=new_assumption)

    elif 'contrary' in request.POST:
        form = ContraryForm(request.POST)
        if form.is_valid():
            new_contrary = form.cleaned_data['contrary']
            controller.extend_framework(framework_name, contrary=new_contrary)

    elif 'random_variable' in request.POST:
        form = RandomVariableForm(request.POST)
        if form.is_valid():
            new_rv = form.cleaned_data['random_variable']
            controller.extend_framework(framework_name, rv=new_rv)

    elif 'rule' in request.POST:
        form = RuleForm(request.POST)
        if form.is_valid():
            new_rule = form.cleaned_data['rule']
            controller.extend_framework(framework_name, rule=new_rule)


def process_settings_form_submission(request, framework_name):
    settings_form = SettingsForm(request.POST)
    s = controller.get_settings(controller.get_user(), framework_name)

    s.enable_trading = True if settings_form.data['enable_trading'] == 'yes' else False
    s.trading_options = settings_form.data['trading_options']
    s.buy_quantity = settings_form.data['buy_quantity']
    s.sell_quantity = settings_form.data['sell_quantity']
    s.required_trade_confidence = settings_form.data['required_trade_confidence']
    s.close_position_yield = settings_form.data['close_position_yield']
    s.close_position_loss_limit = settings_form.data['close_position_loss_limit']
    s.save()


def chart_data(request, instrument_name):
    data = get_json(instrument_name, WEEK)

    return JsonResponse(data)
