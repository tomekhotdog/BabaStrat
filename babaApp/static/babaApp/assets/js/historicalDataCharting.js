POLLING_TIME = 1000 * 60 * 30 // Every 30 mins
PROBABILITY_POLLING_TIME = 1000 * 2 // Once a minute
INSTRUMENT_NAME = ''
DURATION = '/2'
MARKET_DATA_URL = "/babaApp/marketdata/"
INSTRUMENT_NAME = document.getElementById("framework_name").innerHTML

first_graph_drawing = true
INITIAL_ANIMATION_DURATION = 1000
UPDATE_ANIMATION_DURATION = 0

// Polling server for data to populate chart
function setupPolling() {

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

    function fetchProbabilityValues() {
        function onBuyProbabilityReceived(data) {
            document.getElementById('buy_probability_cell').innerHTML = data['semantic_probability']
        }

        function onSellProbabilityReceived(data) {
            document.getElementById('sell_probability_cell').innerHTML = data['semantic_probability']
        }

        URL = MARKET_DATA_URL.concat(INSTRUMENT_NAME).concat(DURATION)
        buy_url = document.getElementById('buy_probability_url').innerHTML
        sell_url = document.getElementById('sell_probability_url').innerHTML

        $.ajax({
            url: buy_url,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                onBuyProbabilityReceived(data)
            }
        });

        $.ajax({
            url: sell_url,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                onSellProbabilityReceived(data)
            }
        });

        setTimeout(fetchProbabilityValues, PROBABILITY_POLLING_TIME)
    }

    fetchData()
    fetchProbabilityValues()
}

var lineChart = null

function drawChart(data) {
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

    setupPolling()
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
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Gross Profit'
                    }
                }]
            }
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
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Gross Profit'
                    }
                }]
            }
        }
    });
}


function strategy_trade_detail(framework){
    var semantic_probabilities_div = document.getElementById("semantic_probabilities_div")
    semantic_probabilities_div.innerHTML = framework

    document.getElementById('strategy_trade_detail_overlay').style.visibility = 'visible'
}

function remove_strategy_trade_detail_overlay() {
    document.getElementById('strategy_trade_detail_overlay').style.visibility = 'hidden'
}



/******************* Trading actions ********************/

function enableTrading() {
    var username = document.getElementById("username").innerHTML;
    var strategy_name = document.getElementById("strategy_name").innerHTML;
    var url = ('strategy_action/').concat(strategy_name).concat('/').concat('enable_trading').concat('/');

    performStrategyAction(url)
}

function disableTrading() {
    var username = document.getElementById("username").innerHTML;
    var strategy_name = document.getElementById("strategy_name").innerHTML;
    var url = ('strategy_action/').concat(strategy_name).concat('/').concat('disable_trading').concat('/');

    performStrategyAction(url)
}

function closePositions() {
    var username = document.getElementById("username").innerHTML;
    var strategy_name = document.getElementById("strategy_name").innerHTML;
    var url = ('strategy_action/').concat(strategy_name).concat('/').concat('close_positions').concat('/');

    performStrategyAction(url)
}

function recalculateProbabilities() {
    var username = document.getElementById("username").innerHTML;
    var strategy_name = document.getElementById("strategy_name").innerHTML;
    var url = ('strategy_action/').concat(strategy_name).concat('/').concat('recalculate_probabilities').concat('/');

    performStrategyAction(url)
}

function performStrategyAction(url) {
    $.ajax({
        url: url,
        method: 'get',
        success: function(data) {
            fetchProbabilityValues()
        }
    });
}

