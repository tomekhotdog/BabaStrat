POLLING_TIME = 20000
INSTRUMENT_NAME = ''
MARKET_DATA_URL = "http://127.0.0.1:8018/babaApp/marketdata/"
INSTRUMENT_NAME = document.getElementById("framework_name").innerHTML

function footerButtonClick() {
    document.getElementById("subheading").innerHTML = "Ohh you've clicked mee....";
}

// Polling server for data to populate chart
function setupChartPolling() {

    function fetchData() {
        function onDataReceived(data) {
              drawChart(data)
        }

        URL = MARKET_DATA_URL.concat(INSTRUMENT_NAME)

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

function drawChart(data) {
    document.getElementById("subheading").innerHTML = "You got me " + (Math.random() * 100).toString();

//    num_elements = data['labels'].length;
//    if (num_elements != MARKET_DATA_ELEMENTS) {
//        alert('here')
//        continue;
//    }
//    MARKET_DATA_ELEMENTS = num_elements

    var ctx = document.getElementById("myChart").getContext("2d");
    var myLineChart = new Chart(ctx).Line(data);
}