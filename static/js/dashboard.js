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
      legend: {
        display: false
      },
      tooltip: {
        boxPadding: 3
      }
    }
  }
});

document.addEventListener("htmx:afterSwap", function(event) {
    if (event.detail.target.id === "chart-container") {
        const response = JSON.parse(event.detail.xhr.response);
        chart.data.labels = response.labels
        chart.data.datasets[0].data = response.data
        chart.data.datasets[1].data = response.data2
        chart.update();
    }
});
