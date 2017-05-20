POLLING_TIME = 20000


function footerButtonClick() {
    document.getElementById("subheading").innerHTML = "Ohh you've clicked mee....";
}

// Polling server for data to populate chart
function setupChartPolling() {
    drawChart()

    function fetchData() {
        function onDataReceived() {
              // Plot the chart with the received data!
        }

        $.ajax({
            url: "http://127.0.0.1:8017/babaApp/data/",
            method: 'GET',
            dataType: 'json',
            success: onDataReceived
        });

        setTimeout(fetchData, POLLING_TIME)
        document.getElementById("subheading").innerHTML = "You got me " + (Math.random() * 100).toString();
    }

    setTimeout(fetchData, POLLING_TIME)

}

function drawChart() {
    var data = {
        labels: ['1', '5', '10', '15', '20', '25', '30', '35', '40', '45'],
        datasets: [
            {
                label: "Site Registrations in the Last 30 Days",
                fillColor: "rgba(220,220,220,0.2)",
                strokeColor: "rgba(220,220,220,1)",
                pointColor: "rgba(226,118,137,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(220,220,220,1)",
                pointHoverBackgroundCover: "rgba(226, 118, 137, 1)",
                pointHoverBorderColor: "rgba(226, 118, 137, 1)",
                lineTension: 0,
                cubicInterpolationMode: 'default',
                data: [12, 4, 7, 7, 2, 9, 4, 8, 13, 20]
            }
        ]
    };
    var ctx = document.getElementById("myChart").getContext("2d");
    var myLineChart = new Chart(ctx).Line(data);
}