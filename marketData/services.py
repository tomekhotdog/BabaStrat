import threading
from marketData import realTime
from babaApp.models import DataSet, DataTick, Framework

TASK_TIME_INTERVAL = 60 * 60  # seconds


class ModuleElements:
    pass

__m = ModuleElements()
__m.subscriptions = set()
__m.task = None
__m.task_is_running = False
__m.data_source = realTime.MarketDataSource()
__m.latest_ticks = {}


# Retrieves latest available tick
def get_latest_tick(symbol):
    if symbol in __m.latest_ticks:
        return __m.latest_ticks[symbol]
    else:
        framework = Framework.objects.get(symbol=symbol)
        latest_tick = DataTick.objects.filter(dataset__dataset_name=framework.framework_name).order_by('-tick_time')[0]
        __m.latest_ticks[symbol] = latest_tick
        return latest_tick


# Subscribe to symbol - periodically query symbol and persist
def subscribe(symbol):
    if symbol not in __m.subscriptions:
        __m.subscriptions.add(symbol)

    if not __m.task_is_running:
        start_querying_task()


# Unsubscribe to symbol - remove from subscriptions list
def unsubscribe(symbol):
    if symbol in __m.subscriptions:
        __m.subscriptions.remove(symbol)

    if len(__m.subscriptions) == 0:
        __m.task.cancel()
        __m.task_running = False


def start_querying_task():
    task = threading.Timer(TASK_TIME_INTERVAL, execute_task)
    task.start()
    __m.task_running = True


def execute_task():
    for symbol in __m.subscriptions:
        tick = __m.data_source.request(symbol)

        try:
            framework = Framework.objects.get(symbol=symbol)
            dataset = DataSet.objects.get(dataset_name=framework.framework_name)
            datatick = DataTick(dataset=dataset, tick_time=tick.time, price=tick.asking_price)
            datatick.save()
            __m.latest_ticks[symbol] = datatick
        except DataSet.DoesNotExist:
            continue

    start_querying_task()

