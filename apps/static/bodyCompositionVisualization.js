let dailyData = {
  date: [],
  weight: [],
  bodyFat: []
};
let monthlyData = {
  date: [],
  weight: [],
  bodyFat: [],
  weightChangeRate: []
};
let chartInstance = null;

async function fetchApiData(apiEndpoint) {
  const response = await fetch(apiEndpoint);
  return await response.json();
}

function populateDailyData(dailyDataSet) {
  dailyData.date = dailyDataSet.map(item => item.date);
  dailyData.weight = dailyDataSet.map(item => item.weight);
  dailyData.bodyFat = dailyDataSet.map(item => item.body_fat);
}

function populateMonthlyData(monthlyDataSet) {
  monthlyData.date = monthlyDataSet.map(item => item.date);
  monthlyData.weight = monthlyDataSet.map(item => item.weight);
  monthlyData.bodyFat = monthlyDataSet.map(item => item.body_fat);
  monthlyData.weightChangeRate = monthlyDataSet.map(item => item.weight_change_rate);
}

function createBodyCompositionGraph(bodyCompositionData) {
  const ctx = document.getElementById("bodyCompositionGraph").getContext("2d");

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: bodyCompositionData.date,
      datasets: [
        {
          label: "体重",
          data: bodyCompositionData.weight,
          yAxisID: "y",
          spanGaps: true,
        },
        {
          label: "体脂肪率",
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
          text: "体重と体脂肪率の推移",
        },
      },
      scales: {
        y: {
          title: {
            display: true,
            text: "体重 (kg)",
          },
        },
        y1: {
          position: "right",
          title: {
            display: true,
            text: "体脂肪率 (%)",
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
    return ["平均体重 (kg)", "平均体脂肪率 (%)"];
  } else if (granularity === "daily") {
    return ["体重 (kg)", "体脂肪率 (%)"];
  }
}

function createTableHeader(weightHeader, bodyFatHeader, granularity) {
  let tableHtml = `
    <thead>
      <tr>
        <th>日付</th>
        <th>${weightHeader}</th>
        <th>${bodyFatHeader}</th>
  `;
  if (granularity === "monthly") {
    tableHtml += `<th>先月比の変化率 (%)</th>`;
  }
  tableHtml += `</tr></thead>`;
  return tableHtml;
}

function sortIndicesByDateDesc(dates) {
  const dateObjects = dates.map(date => new Date(date));
  return dateObjects.map((_, index) => index).sort((a, b) => dateObjects[b] - dateObjects[a]);
}

function createTableData(bodyCompositionData, sortedIndices, granularity) {
  let tableHtml = '<tbody>';
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
  tableHtml += '</tbody>';
  return tableHtml;
}

function updateBodyCompositionTable(bodyCompositionData, granularity) {
  const table = document.getElementById("body-composition-table");
  const [weightHeader, bodyFatHeader] = getHeaders(granularity);
  const tableHeaderHtml = createTableHeader(weightHeader, bodyFatHeader, granularity);
  const sortedIndicesDesc = sortIndicesByDateDesc(bodyCompositionData.date);
  const tableDataHtml = createTableData(bodyCompositionData, sortedIndicesDesc, granularity);
  table.innerHTML = tableHeaderHtml + tableDataHtml;
}


async function initializePage() {
  const body_composition_data = await fetchApiData("/get_body_composition_data");
  populateDailyData(body_composition_data[0]);
  populateMonthlyData(body_composition_data[1]);

  const durationValue = parseInt(document.getElementById("duration-dropdown").value);
  const granularityValue = document.getElementById("granularity-dropdown").value;
  const filteredBodyCompositionData = filterBodyCompositionDataByDuration(dailyData, durationValue);
  createBodyCompositionGraph(filteredBodyCompositionData);
  updateBodyCompositionTable(filteredBodyCompositionData, granularityValue);
}
window.onload = initializePage();

function handleGranularityChange() {
  const granularityValue = this.value;
  const durationValue = parseInt(document.getElementById("duration-dropdown").value);

  let targetData;
  if (granularityValue === "daily") {
    targetData = dailyData;
  } else if (granularityValue === "monthly") {
    targetData = monthlyData;
  }
  const filteredData = filterBodyCompositionDataByDuration(targetData, durationValue);

  updateBodyCompositionGraph(filteredData, granularityValue);
  updateBodyCompositionTable(filteredData, granularityValue);
}

function getLabelsByGranularity(granularity) {
  if (granularity === "monthly") {
    return { weightLabel: "平均体重", bodyFatLabel: "平均体脂肪率" };
  } else if (granularity === "daily") {
    return { weightLabel: "体重", bodyFatLabel: "体脂肪率" };
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

function updateBodyCompositionGraph(bodyCompositionData, granularity) {
  const { weightLabel, bodyFatLabel } = getLabelsByGranularity(granularity);
  updateGraphLabels(chartInstance, weightLabel, bodyFatLabel);
  updateGraphData(chartInstance, bodyCompositionData);
  chartInstance.update();
}


function filterBodyCompositionDataByDuration(BodyCompositionData, days, granularity) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const filteredIndices = BodyCompositionData.date.map((d, index) => (new Date(d) >= cutoffDate) ? index : -1).filter(index => index !== -1);

  const filteredData = {
    date: filteredIndices.map(index => BodyCompositionData.date[index]),
    weight: filteredIndices.map(index => BodyCompositionData.weight[index]),
    bodyFat: filteredIndices.map(index => BodyCompositionData.bodyFat[index])
  };

  if (granularity === "monthly") {
    filteredData.weightChangeRate = filteredIndices.map(index => BodyCompositionData.weightChangeRate[index]);
  }
  return filteredData;
}

// TODO メソッド分けしたいかも。
function handleGranularityChange() {
  const granularityValue = this.value;
  let options = [
    { value: "7", label: "1週間" },
    { value: "30", label: "1か月" },
    { value: "90", label: "3か月" },
    { value: "180", label: "半年" },
    { value: "365", label: "1年" },
    { value: "1095", label: "3年" }
  ];

  // 表示粒度に応じて、表示期間のオプションを変更し、その初期値を設定する。
  let defaultGranularityValue;
  if (granularityValue === "monthly") {
    options = options.filter(opt => opt.value !== "7");
    defaultGranularityValue = "365";
  } else {
    defaultGranularityValue = "30";
  }

  // 変更した表示オプションを反映する。
  const durationDropdown = document.getElementById("duration-dropdown");
  durationDropdown.innerHTML = options.map(opt => {
    let selected = opt.value === defaultGranularityValue ? ' selected' : '';
    return `<option value="${opt.value}"${selected}>${opt.label}</option>`;
  }).join('');

  // 表示粒度に応じて、グラフを更新する。
  const durationValue = parseInt(document.getElementById("duration-dropdown").value);
  const targetData = granularityValue === "daily" ? dailyData : monthlyData;
  const filteredData = filterBodyCompositionDataByDuration(targetData, durationValue, granularityValue);

  // グラフとテーブルを更新
  updateBodyCompositionGraph(filteredData, granularityValue);
  updateBodyCompositionTable(filteredData, granularityValue);
}
document.getElementById("granularity-dropdown").addEventListener("change", handleGranularityChange);

// TODO メソッド名を考えないとなあ。
function handleDurationChange() {
  const granularityValue = document.getElementById("granularity-dropdown").value;
  const durationValue = parseInt(this.value);
  const targetData = granularityValue === "daily" ? dailyData : monthlyData;
  const filteredData = filterBodyCompositionDataByDuration(targetData, durationValue, granularityValue);

  // グラフとテーブルを更新
  updateBodyCompositionGraph(filteredData, granularityValue);
  updateBodyCompositionTable(filteredData, granularityValue);
}
document.getElementById("duration-dropdown").addEventListener("change", handleDurationChange);