import threading
from marketData import realTime
from babaApp.models import DataSet, DataTick, Framework


TASK_TIME_INTERVAL = 60 * 60  # seconds


class QueryingMarketDataService:

    def __init__(self):
        self.subscriptions = set()
        self.task = None
        self.task_running = False
        self.data_source = realTime.MarketDataSource()
        self.latest_ticks = {}

    # Retrieves latest available tick
    def get_latest_tick(self, symbol):
        if symbol in self.latest_ticks:
            return self.latest_ticks[symbol]
        else:
            framework = Framework.objects.get(symbol=symbol)
            latest_tick = DataTick.objects.filter(dataset__dataset_name=framework.framework_name).order_by('-tick_time')[0]
            self.latest_ticks[symbol] = latest_tick
            return latest_tick

    # Subscribe to symbol - periodically query symbol and persist
    def subscribe(self, symbol):
        if symbol not in self.subscriptions:
            self.subscriptions.add(symbol)

        if not self.task_running:
            self.start_querying_task()

    # Unsubscribe to symbol - remove from subscriptions list
    def unsubscribe(self, symbol):
        if symbol in self.subscriptions:
            self.subscriptions.remove(symbol)

        if len(self.subscriptions) == 0:
            self.task.cancel()
            self.task_running = False

    def start_querying_task(self):
        self.task = threading.Timer(TASK_TIME_INTERVAL, self.execute_task)
        self.task.start()
        self.task_running = True

    def execute_task(self):
        for symbol in self.subscriptions:
            tick = self.data_source.request(symbol)

            try:
                framework = Framework.objects.get(symbol=symbol)
                dataset = DataSet.objects.get(dataset_name=framework.framework_name)
                datatick = DataTick(dataset=dataset, tick_time=tick.time, price=tick.asking_price)
                datatick.save()
                self.latest_ticks[symbol] = datatick
            except DataSet.DoesNotExist:
                continue

        self.start_querying_task()


