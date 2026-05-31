import { getGranularityConfig } from "./bodyCompositionConfig.js";

let chart = null;
let chartUnavailable = false;

function toChartData(records) {
  return {
    labels: records.map((record) => record.date),
    weight: records.map((record) => record.weight),
    bodyFat: records.map((record) => record.bodyFat),
  };
}

function canRenderChart() {
  if (typeof Chart !== "undefined") {
    return true;
  }

  if (!chartUnavailable) {
    console.error("Chart.js is unavailable.");
    chartUnavailable = true;
  }
  return false;
}

function createChart(canvasElement, records, granularity) {
  if (!canRenderChart()) {
    return;
  }

  const config = getGranularityConfig(granularity);
  const chartData = toChartData(records);
  const ctx = canvasElement.getContext("2d");

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: config.weightLabel,
          data: chartData.weight,
          yAxisID: "y",
          spanGaps: true,
        },
        {
          label: config.bodyFatLabel,
          data: chartData.bodyFat,
          yAxisID: "y1",
          spanGaps: true,
        },
      ],
    },
    options: {
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        title: {
          display: true,
          text: "Trends in Weight and Body Fat Percentage",
        },
      },
      scales: {
        y: {
          title: {
            display: true,
            text: "Weight (kg)",
          },
        },
        y1: {
          position: "right",
          title: {
            display: true,
            text: "Body Fat Percentage (%)",
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
  });
}

export function updateChart(canvasElement, records, granularity) {
  if (!canRenderChart()) {
    return;
  }

  if (chart === null) {
    createChart(canvasElement, records, granularity);
    return;
  }

  const config = getGranularityConfig(granularity);
  const chartData = toChartData(records);
  chart.data.labels = chartData.labels;
  chart.data.datasets[0].label = config.weightLabel;
  chart.data.datasets[0].data = chartData.weight;
  chart.data.datasets[1].label = config.bodyFatLabel;
  chart.data.datasets[1].data = chartData.bodyFat;
  chart.update();
}
