POLLING_TIME = 20000
INSTRUMENT_NAME = ''
DURATION = '/2'
MARKET_DATA_URL = "/babaApp/marketdata/"
INSTRUMENT_NAME = document.getElementById("framework_name").innerHTML

first_graph_drawing = true
INITIAL_ANIMATION_DURATION = 1000
UPDATE_ANIMATION_DURATION = 0

function footerButtonClick() {
    document.getElementById("test_element").innerHTML = "Ohh you've clicked mee....";
}

// Polling server for data to populate chart
function setupChartPolling() {

    function fetchData() {
        function onDataReceived(data) {
            drawChart(data)
        }

        URL = MARKET_DATA_URL.concat(INSTRUMENT_NAME).concat(DURATION)

        $.ajax({
            url: URL,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                onDataReceived(data)
            }
        });

        setTimeout(fetchData, POLLING_TIME)
    }

    fetchData()
}

var lineChart = null

function drawChart(data) {
    document.getElementById("test_element").innerHTML = "test element: " + (Math.random() * 100).toString();

    if (lineChart != null) {
        lineChart.destroy()
    }

    animation_duration = first_graph_drawing ? INITIAL_ANIMATION_DURATION : UPDATE_ANIMATION_DURATION

    var ctx = document.getElementById("myChart").getContext("2d");
    myLineChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            layout: {
                padding: {
                    left: 10,
                    right: 0,
                    top: 0,
                    bottom: 0
                }
            },
            animation: {
                duration: animation_duration
            }
        }
    });

    first_graph_drawing = false

}

function chartView(id) {
    first_graph_drawing = true

    if (id == 'day') {
        DURATION = '/1'
    } else if (id == 'week') {
        DURATION = '/2'
    } else if (id == 'month') {
        DURATION = '/3'
    } else if (id == '3mth') {
        DURATION = '/4'
    }

    setupChartPolling()
}

// URLs to be encoded in hidden html elements, set through POST submissions
//strategy_performance_data_url = document.getElementById("strategy_performance_data_url").innerHTML
//back_test_data_url = document.getElementById("back_test_data_url").innerHTML

function setupAnalyseCharts() {
    username = document.getElementById("username").innerHTML
    strategy_name = document.getElementById("strategy_name").innerHTML

    getPerformanceChartData(username, strategy_name)
    getBackTestChartData(username, strategy_name)
}

function getPerformanceChartData(username, strategy_name) {
    URL = document.getElementById("strategy_performance_data_url").innerHTML
    $.ajax({
        url: URL,
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            drawPerformanceChart(data)
        }
    });
}

function getBackTestChartData(username, strategy_name) {
    URL = document.getElementById("back_test_data_url").innerHTML
    $.ajax({
        url: URL,
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            drawBackTestChart(data)
        }
    });
}

function drawPerformanceChart(data) {
    var ctx = document.getElementById("performanceChart").getContext("2d");
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 0,
                    bottom: 0
                }
            },
        }
    });
}

function drawBackTestChart(data) {
    var ctx = document.getElementById("backTestChart").getContext("2d");
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 0,
                    bottom: 0
                }
            },
        }
    });
}