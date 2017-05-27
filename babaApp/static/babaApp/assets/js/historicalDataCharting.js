POLLING_TIME = 20000
INSTRUMENT_NAME = ''
MARKET_DATA_URL = "http://127.0.0.1:8021/babaApp/marketdata/"
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

var lineChart = null

function drawChart(data) {
    document.getElementById("subheading").innerHTML = "You got me " + (Math.random() * 100).toString();


    if (lineChart != null) {
        lineChart.destroy()
    }

    var ctx = document.getElementById("myChart").getContext("2d");
    lineChart = new Chart(ctx).Line(data, {
        responsive: true,
        maintainAspectRatio: true
    });


}