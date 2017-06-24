import threading
from betfair_wrapper import markets_discovery
from babaApp.models import ExchangeEvent

RECALCULATION_INTERVAL = 300  # Every 5 minutes
FLOAT_FORMAT = "{0:.2f}"


class ModuleElements:
    pass


__m = ModuleElements()
__m.discovery_task = None
__m.task_is_running = False


def start_strategy_task():
    if not __m.task_is_running:
        execute_discovery_task()


def stop_strategy_task():
    if __m.task_is_running:
        __m.discovery_task.cancel()
        __m.task_is_running = False


# Updates the semantic probabilities of BUY and SELL sentences in all frameworks
def execute_discovery_task():
    discover_random_variables()

    __m.strategy_task = threading.Timer(RECALCULATION_INTERVAL, execute_discovery_task)
    __m.strategy_task.start()
    __m.task_is_running = True


def discover_random_variables():
    event_objects = markets_discovery.get_event_probabilities()

    ExchangeEvent.objects.all().delete()

    for event_id, event_object in event_objects.items():
        event_name_string = str(event_object).replace('.', '_')
        event_name_string = event_name_string.replace('+', 'plus')
        event_name_string = event_name_string.replace('-', 'minus')

        new_event = ExchangeEvent(
            event_name=event_name_string,
            probability=FLOAT_FORMAT.format(event_object.probability)
        )
        new_event.save()