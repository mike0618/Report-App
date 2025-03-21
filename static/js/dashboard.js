let eventSource = null; // Global reference to the SSE connection

async function receive() {
    var ctx = document.getElementById("myChart").getContext("2d");
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#007bff',
                borderWidth: 4,
                pointBackgroundColor: '#007bff',
                cubicInterpolationMode: 'monotone',
            },
            {
                data: [],
                lineTension: 0,
                backgroundColor: 'transparent',
                borderColor: '#ff7bff',
                borderWidth: 4,
                pointBackgroundColor: '#ff7bff',
                cubicInterpolationMode: 'monotone',
            }]
        },
        options: {
            plugins: {
                legend: { display: false },
                tooltip: { boxPadding: 3 }
            }
        }
    });

    // Close any existing SSE connection before starting a new one
    if (eventSource) {
        eventSource.close();
    }

    // Establish a new SSE connection
    eventSource = new EventSource("/stream");

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Received: ", data);
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.data;
        chart.data.datasets[1].data = data.data2;
        chart.update();
    };
}

// Start the SSE when #myChart is present
document.body.addEventListener('htmx:afterSwap', function () {
    if (document.getElementById("myChart")) {
        receive();
    }
});

// Stop the SSE when #myChart is removed
document.body.addEventListener('htmx:beforeSwap', function () {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
        console.log("SSE connection closed.");
    }
});

