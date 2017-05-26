import threading
from babaSemantics.Semantics import GROUNDED, SCEPTICALLY_PREFERRED, IDEAL
from babaSemantics.Semantics import compute_semantic_probability
import babaSemantics.BABAProgramParser as Parser
from babaApp.models import Framework, TradingSettings, Trade
from babaApp.databaseController import controller

RECALCULATION_INTERVAL = 30

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
    __m.strategy_task = threading.Timer(RECALCULATION_INTERVAL, execute_strategy_task)
    __m.strategy_task.start()
    __m.task_is_running = True


# Updates the semantic probabilities of BUY and SELL sentences in all frameworks
def execute_strategy_task():
    user = controller.get_user()

    update_semantic_probabilities()
    perform_open_position_trades(user)
    perform_close_position_trades(user) # TODO: can only be affected by change in price
    start_strategy_task()


# Iterates through frameworks and recalculates the semantic probabilities
def update_semantic_probabilities():
    frameworks = Framework.objects.all()
    for framework in frameworks:
        framework_name = framework.framework_name
        framework_string = framework.string_representation
        baba = Parser.BABAProgramParser(string=framework_string).parse()

        g_probabilities = compute_semantic_probability(GROUNDED, baba)
        s_probabilities = compute_semantic_probability(SCEPTICALLY_PREFERRED, baba)
        i_probabilities = compute_semantic_probability(IDEAL, baba)

        store_probability_tuples = [(__m.grounded_probabilities, g_probabilities),
                                    (__m.sceptically_preferred_probabilities, s_probabilities),
                                    (__m.ideal_probabilities, i_probabilities)]

        for (store, probabilities) in store_probability_tuples:
            store[framework_name + '_' + BUY] = \
                probabilities[BUY] if BUY in probabilities.keys() else 0
            store[framework_name + '_' + BUY] = \
                probabilities[BUY] if BUY in probabilities.keys() else 0


# Analyses semantic probabilities, cross referencing with
#  user thresholds and executes trades as required.
def perform_open_position_trades(user):
    frameworks = Framework.objects.all()
    for framework in frameworks:
        try:
            user_trading_settings = TradingSettings.objects.get(user=user, framework_name=framework)
            if not user_trading_settings.enable_trading:
                continue

            for direction in [BUY, SELL]:
                if user_already_holds_position(user, framework, direction):
                    continue

                key = framework.framework_name + '_' + direction
                if key in __m.grounded_probabilities.keys() and \
                   __m.grounded_probabilities[key] >= user_trading_settings.required_trade_confidence:
                    execute_open_position(user, framework, direction)

        except TradingSettings.DoesNotExist:
            continue


# Analyses open positions and closes them if required
# (with respect to to the required yield or loss limit)
def perform_close_position_trades(user):
    open_positions = Trade.objects.filter(portfolio__user=user, open_position=True)
    for open_position in open_positions:
        user_trading_settings = TradingSettings.objects.get(user=user, framework_name=open_position.framework_name)

        initial_value = open_position.price * open_position.quantity
        current_value = 0 * open_position.quantity #TODO: get latest price.

        # yield threshold reached
        if ((current_value - initial_value) / initial_value * 100) >= user_trading_settings.close_position_yield:
            execute_close_position(open_position)

        # loss limit reached
        elif ((initial_value - current_value) / initial_value * 100) >= user_trading_settings.close_position_loss_limit:
            execute_close_position(open_position)


def user_already_holds_position(user, framework, direction):
    # TODO: returns whether user has an exisitng non-closed position for particular framework and direction
    return False


def execute_open_position(user, framework, direction):
    # TODO: execute trade (look up latest price, save db object)
    pass


def execute_close_position(open_position):
    # TODO: get latest_price, update object, save()
    pass


def get_probability(framework_name, direction, semantics):
    key = framework_name + '_' + direction

    if semantics == GROUNDED and key in __m.grounded_probabilities.keys():
        return __m.grounded_probabilities[key]
    elif semantics == SCEPTICALLY_PREFERRED and key in __m.sceptically_preferred_probabilities.keys():
        return __m.sceptically_preferred_probabilities[key]
    elif semantics == IDEAL and key in __m.ideal_probabilities.keys():
        return __m.ideal_probabilities[key]
    else:
        return 0  # Raise exception?