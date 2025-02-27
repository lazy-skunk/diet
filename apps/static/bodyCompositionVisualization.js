let dailyData = {
  date: [],
  weight: [],
  bodyFat: [],
};
let monthlyData = {
  date: [],
  weight: [],
  bodyFat: [],
  weightChangeRate: [],
};
let chartInstance = null;

async function fetchApiData(apiEndpoint) {
  const response = await fetch(apiEndpoint);
  return await response.json();
}

function populateDailyData(dailyDataSet) {
  dailyData.date = dailyDataSet.map((item) => item.date);
  dailyData.weight = dailyDataSet.map((item) => item.weight);
  dailyData.bodyFat = dailyDataSet.map((item) => item.body_fat);
}

function populateMonthlyData(monthlyDataSet) {
  monthlyData.date = monthlyDataSet.map((item) => item.date);
  monthlyData.weight = monthlyDataSet.map((item) => item.weight);
  monthlyData.bodyFat = monthlyDataSet.map((item) => item.body_fat);
  monthlyData.weightChangeRate = monthlyDataSet.map(
    (item) => item.weight_change_rate
  );
}

function createGraph(bodyCompositionData) {
  const ctx = document.getElementById("bodyCompositionGraph").getContext("2d");

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: bodyCompositionData.date,
      datasets: [
        {
          label: "Weight",
          data: bodyCompositionData.weight,
          yAxisID: "y",
          spanGaps: true,
        },
        {
          label: "Body Fat Percentage",
          data: bodyCompositionData.bodyFat,
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

function getHeaders(granularity) {
  if (granularity === "monthly") {
    return ["Average Weight (kg)", "Average Body Fat Percentage (%)"];
  } else if (granularity === "daily") {
    return ["Weight (kg)", "Body Fat Percentage (%)"];
  }
}

function createTableHeader(weightHeader, bodyFatHeader, granularity) {
  let tableHtml = `
    <thead>
      <tr>
        <th>Date</th>
        <th>${weightHeader}</th>
        <th>${bodyFatHeader}</th>
  `;
  if (granularity === "monthly") {
    tableHtml += `<th>Change Rate from Last Month (%)</th>`;
  }
  tableHtml += `</tr></thead>`;
  return tableHtml;
}

function sortIndicesByDateDesc(dates) {
  const dateObjects = dates.map((date) => new Date(date));
  return dateObjects
    .map((_, index) => index)
    .sort((a, b) => dateObjects[b] - dateObjects[a]);
}

function createTableData(bodyCompositionData, sortedIndices, granularity) {
  let tableHtml = "<tbody>";
  for (const i of sortedIndices) {
    tableHtml += `
      <tr>
        <td>${bodyCompositionData.date[i]}</td>
        <td>${bodyCompositionData.weight[i]}</td>
        <td>${bodyCompositionData.bodyFat[i]}</td>
    `;
    if (granularity === "monthly") {
      tableHtml += `<td>${bodyCompositionData.weightChangeRate[i]}</td>`;
    }
    tableHtml += `</tr>`;
  }
  tableHtml += "</tbody>";
  return tableHtml;
}

function updateTable(bodyCompositionData, granularity) {
  const table = document.getElementById("body-composition-table");
  const [weightHeader, bodyFatHeader] = getHeaders(granularity);
  const tableHeaderHtml = createTableHeader(
    weightHeader,
    bodyFatHeader,
    granularity
  );
  const sortedIndicesDesc = sortIndicesByDateDesc(bodyCompositionData.date);
  const tableDataHtml = createTableData(
    bodyCompositionData,
    sortedIndicesDesc,
    granularity
  );
  table.innerHTML = tableHeaderHtml + tableDataHtml;
}

async function loadDataAndRender() {
  const body_composition_data = await fetchApiData(
    "body_composition/get_body_composition_data"
  );
  populateDailyData(body_composition_data[0]);
  populateMonthlyData(body_composition_data[1]);

  const durationValue = parseInt(
    document.getElementById("duration-dropdown").value
  );
  const granularityValue = document.getElementById(
    "granularity-dropdown"
  ).value;
  const filteredBodyCompositionData = filterDataByDuration(
    dailyData,
    durationValue
  );

  createGraph(filteredBodyCompositionData);
  updateTable(filteredBodyCompositionData, granularityValue);
}
window.onload = loadDataAndRender();

function getTargetData(granularityValue) {
  if (granularityValue === "monthly") {
    return monthlyData;
  } else if (granularityValue === "daily") {
    return dailyData;
  }
  return null;
}

function handleGranularityChange() {
  const granularityValue = this.value;
  const durationValue = parseInt(
    document.getElementById("duration-dropdown").value
  );

  const targetBodyCompositionData = getTargetData(granularityValue);
  const filteredData = filterDataByDuration(
    targetBodyCompositionData,
    durationValue
  );

  updateGraph(filteredData, granularityValue);
  updateTable(filteredData, granularityValue);
}

function getLabelsByGranularity(granularity) {
  if (granularity === "monthly") {
    return {
      weightLabel: "Average Weight",
      bodyFatLabel: "Average Body Fat Percentage",
    };
  } else if (granularity === "daily") {
    return { weightLabel: "Weight", bodyFatLabel: "Body Fat Percentage" };
  }
}

function updateGraphLabels(chartInstance, weightLabel, bodyFatLabel) {
  chartInstance.data.datasets[0].label = weightLabel;
  chartInstance.data.datasets[1].label = bodyFatLabel;
}

function updateGraphData(chartInstance, bodyCompositionData) {
  chartInstance.data.labels = bodyCompositionData.date;
  chartInstance.data.datasets[0].data = bodyCompositionData.weight;
  chartInstance.data.datasets[1].data = bodyCompositionData.bodyFat;
}

function updateGraph(bodyCompositionData, granularity) {
  const { weightLabel, bodyFatLabel } = getLabelsByGranularity(granularity);
  updateGraphLabels(chartInstance, weightLabel, bodyFatLabel);
  updateGraphData(chartInstance, bodyCompositionData);
  chartInstance.update();
}
function calculateCutoffDate(days) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  return cutoffDate;
}

function getFilteredIndices(dates, cutoffDate) {
  const indices = [];
  for (let i = 0; i < dates.length; i++) {
    if (new Date(dates[i]) >= cutoffDate) {
      indices.push(i);
    }
  }
  return indices;
}

function generateFilteredData(
  BodyCompositionData,
  filteredIndices,
  granularity
) {
  const filteredData = {
    date: filteredIndices.map((index) => BodyCompositionData.date[index]),
    weight: filteredIndices.map((index) => BodyCompositionData.weight[index]),
    bodyFat: filteredIndices.map((index) => BodyCompositionData.bodyFat[index]),
  };

  if (granularity === "monthly") {
    filteredData.weightChangeRate = filteredIndices.map(
      (index) => BodyCompositionData.weightChangeRate[index]
    );
  }

  return filteredData;
}

function filterDataByDuration(BodyCompositionData, days, granularity) {
  const cutoffDate = calculateCutoffDate(days);
  const filteredIndices = getFilteredIndices(
    BodyCompositionData.date,
    cutoffDate
  );
  return generateFilteredData(
    BodyCompositionData,
    filteredIndices,
    granularity
  );
}

function updateDurationOptions(granularityValue) {
  let options = [
    { value: "7", label: "7 Days" },
    { value: "30", label: "30 Days" },
    { value: "90", label: "90 Days" },
    { value: "180", label: "180 Days" },
    { value: "365", label: "1 Year" },
    { value: "1095", label: "3 Years" },
  ];

  let selectedGranularityValue;
  if (granularityValue === "monthly") {
    options = options.filter((opt) => opt.value !== "7");
    selectedGranularityValue = "365";
  } else if (granularityValue === "daily") {
    selectedGranularityValue = "30";
  }

  const durationDropdown = document.getElementById("duration-dropdown");
  durationDropdown.innerHTML = options
    .map((opt) => {
      let selected = opt.value === selectedGranularityValue ? " selected" : "";
      return `<option value="${opt.value}"${selected}>${opt.label}</option>`;
    })
    .join("");
}

function updateGraphAndTable(granularityValue) {
  const durationValue = parseInt(
    document.getElementById("duration-dropdown").value
  );
  const targetData = getTargetData(granularityValue);
  const filteredData = filterDataByDuration(
    targetData,
    durationValue,
    granularityValue
  );
  updateGraph(filteredData, granularityValue);
  updateTable(filteredData, granularityValue);
}

function handleGranularityChange() {
  const granularityValue = this.value;
  updateDurationOptions(granularityValue);
  updateGraphAndTable(granularityValue);
}
document
  .getElementById("granularity-dropdown")
  .addEventListener("change", handleGranularityChange);

function handleDurationChange() {
  const granularityValue = document.getElementById(
    "granularity-dropdown"
  ).value;
  const durationValue = parseInt(this.value);
  const targetData = getTargetData(granularityValue);
  const filteredData = filterDataByDuration(
    targetData,
    durationValue,
    granularityValue
  );
  updateGraph(filteredData, granularityValue);
  updateTable(filteredData, granularityValue);
}
document
  .getElementById("duration-dropdown")
  .addEventListener("change", handleDurationChange);
