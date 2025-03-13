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

// SSE connection
const eventSource = new EventSource("/stream");
eventSource.onmessage = function(event){
  const data = JSON.parse(event.data);
  console.log("Received: ", data);
  chart.data.labels = data.labels
  chart.data.datasets[0].data = data.data
  chart.data.datasets[1].data = data.data2
  chart.update();
};

