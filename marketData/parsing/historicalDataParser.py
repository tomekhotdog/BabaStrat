from babaApp.models import *
from datetime import datetime
from decimal import DecimalException
import csv

# Parsing CSV files from: http://fxhistoricaldata.com/
# file format: symbol, datetime, price 1, price 2, price 3, price 4
# '2015-10-12 15:00:00'
# (price 2 is always the highest value, assume = bid price)
def parse_csv(file_location):
    with open(file_location, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            symbol = row[0]
            currency_symbol = symbol[0:3] + '-' + symbol[3:]

            time = row[1]
            date_elem = time.split(' ')[0]
            date_elements = date_elem.split('-')
            year = int(date_elements[0])
            month = int(date_elements[1])
            day = int(date_elements[2])

            time_elem = time.split(' ')[1]
            time_elements = time_elem.split(':')
            hour = int(time_elements[0])
            minutes = int(time_elements[1])
            seconds = int(time_elements[2])

            datatick_time = datetime(year, month, day, hour, minutes, seconds)

            price = float(row[3])

            dataset_objects = DataSet.objects.filter(dataset_name=currency_symbol)
            dataset_object = None
            if len(dataset_objects) == 0:
                dataset_object = DataSet(dataset_name=currency_symbol)
                dataset_object.save()
            else:
                dataset_object = dataset_objects[0]

            datatick_object = DataTick(dataset=dataset_object, tick_time=datatick_time, price=price)
            try:
                datatick_object.save()
            except DecimalException:
                "Error when saving object (DecimalException)"
            except RuntimeError:
                "Error when saving object (RuntimeError)"


def parse_all_csv_files():
    currencies = ['AUDJPY', 'AUDUSD', 'CHFJPY', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPCHF',
             'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY', 'XAGUSD', 'XAUUSD']

    for currency in currencies:
        filename = "../historicalData/" + currency + "_hour.csv"
        parse_csv(filename)

