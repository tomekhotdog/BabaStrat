from datetime import date, datetime, timedelta


def get_default_strategy_performance_start_date():
    return datetime.now() - timedelta(7)


def get_default_strategy_performance_end_date():
    return datetime.now()


def get_default_back_test_start_date():
    return datetime.now() - timedelta(30)


def get_default_back_test_end_date():
    return datetime.now()


def get_strategy_performance_data_url(username, strategy_name, start_date, end_date):
    time_interval_url_string = get_time_interval_string(start_date, end_date)

    return '/babaApp/data/performance/' + username + '/' + strategy_name + '/' + time_interval_url_string


def get_back_test_data_url(username, strategy_name, start_date, end_date):
    time_interval_url_string = get_time_interval_string(start_date, end_date)

    return '/babaApp/data/back_test/' + username + '/' + strategy_name + '/' + time_interval_url_string


def get_default_back_test_data_url():
    return '/babaApp/data/empty/'


def get_time_interval_string(start_date, end_date):
    start_date_time = datetime.combine(start_date, datetime.min.time())
    end_date_time = datetime.combine(end_date, datetime.min.time())

    start_seconds = start_date_time.timestamp()
    end_seconds = end_date_time.timestamp()

    return str(start_seconds) + '/' + str(end_seconds)
