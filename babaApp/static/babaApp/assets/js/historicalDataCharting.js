POLLING_TIME = 20000
INSTRUMENT_NAME = ''
DURATION = '/2'
MARKET_DATA_URL = "http://127.0.0.1:8042/babaApp/marketdata/"
INSTRUMENT_NAME = document.getElementById("framework_name").innerHTML

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

//        setTimeout(fetchData, POLLING_TIME)
    }

    fetchData()
}

var lineChart = null

function drawChart(data) {
    document.getElementById("test_element").innerHTML = "test element: " + (Math.random() * 100).toString();

    if (lineChart != null) {
//        lineChart.destroy()
    }

    var ctx = document.getElementById("myChart").getContext("2d");
    lineChart = new Chart(ctx)
    lineChart.Line(data, {
        responsive: true,
        maintainAspectRatio: true,
//        animation: false
    });
}

function chartView(id) {
    if (id == 'day') {
        DURATION = '/1'
    } else if (id == 'week') {
        DURATION = '/2'
    } else if (id == 'month') {
        DURATION = '/3'
    } else if (id == '3mnth') {
        DURATION = '/4'
    }

    resetCanvas()
    setupChartPolling()
}

function resetCanvas() {
  $('#myChart').remove(); // this is my <canvas> element
  $('#chart_div').append('<canvas id="myChart"><canvas>');
  canvas = document.querySelector('#myChart');
  ctx = canvas.getContext('2d');
  ctx.canvas.width = 800 //$('#chart_section').width(); // resize to parent width
  ctx.canvas.height = 300 // $('#chart_section').height(); // resize to parent height
  var x = canvas.width/2;
  var y = canvas.height/2;
//  ctx.font = '10pt Verdana';
//  ctx.textAlign = 'center';
//  ctx.fillText('This text is centered on the canvas', x, y);
};