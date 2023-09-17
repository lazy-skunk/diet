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

async function fetchBodyCompositionData() {
  const response = await fetch("/get_body_composition_data");
  const body_composition_data = await response.json();

  const dailyDataSet = body_composition_data[0];
  dailyData.date = dailyDataSet.map(item => item.date);
  dailyData.weight = dailyDataSet.map(item => item.weight);
  dailyData.bodyFat = dailyDataSet.map(item => item.body_fat);

  const monthlyDataSet = body_composition_data[1];
  monthlyData.date = monthlyDataSet.map(item => item.date);
  monthlyData.weight = monthlyDataSet.map(item => item.weight);
  monthlyData.bodyFat = monthlyDataSet.map(item => item.body_fat);
  monthlyData.weightChangeRate = monthlyDataSet.map(item => item.weight_change_rate);
}

function createGraph(bodyCompositionData) {
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
          pointRadius: 0,
          pointHoverRadius: 0
        },
        {
          label: "体脂肪率",
          data: bodyCompositionData.bodyFat,
          yAxisID: "y1",
          spanGaps: true,
          pointRadius: 0,
          pointHoverRadius: 0
        },
      ],
    },
    options: {
      responsive: true,
      interaction: {
        mode: "index",
        intersect: false,
      },
      stacked: false,
      plugins: {
        title: {
          display: true,
          text: "体重と体脂肪率の推移",
        },
      },
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: {
            display: true,
            text: "体重 (kg)",
          },
        },
        y1: {
          type: "linear",
          display: true,
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

// 体組成情報のテーブルを更新する関数
function updateBodyCompositionTable(data, granularity) {
  const table = document.getElementById("body-composition-table");

  let weightHeader = granularity === "monthly" ? "平均体重 (kg)" : "体重 (kg)";
  let bodyFatHeader = granularity === "monthly" ? "平均体脂肪率 (%)" : "体脂肪率 (%)";

  const sortedIndices = data.date.map((date, index) => index).sort((a, b) => new Date(data.date[b]) - new Date(data.date[a]));

  let tableHtml = `
    <thead>
      <tr>
        <th>日付</th>
        <th>${weightHeader}</th>
        <th>${bodyFatHeader}</th>
      </tr>
    </thead>
    <tbody>
  `;

  for (const i of sortedIndices) {
    tableHtml += `
      <tr>
        <td>${data.date[i]}</td>
        <td>${data.weight[i]}</td>
        <td>${data.bodyFat[i]}</td>
      </tr>
    `;
  }

  tableHtml += '</tbody>';
  table.innerHTML = tableHtml;
}


async function initializePage() {
  await fetchBodyCompositionData();
  const durationValue = parseInt(document.getElementById("duration-dropdown").value);
  const granularityValue = document.getElementById("granularity-dropdown").value;
  const filteredBodyCompositionData = filterBodyCompositionDataByDuration(dailyData, durationValue);
  createGraph(filteredBodyCompositionData);
  updateBodyCompositionTable(filteredBodyCompositionData, granularityValue);
}
window.onload = initializePage();

function updateGraph(data) {
  chartInstance.data.labels = data.date;
  chartInstance.data.datasets[0].data = data.weight;
  chartInstance.data.datasets[1].data = data.bodyFat;
  chartInstance.update();
}

function filterBodyCompositionDataByDuration(BodyCompositionData, days) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const filteredIndices = BodyCompositionData.date.map((d, index) => (new Date(d) >= cutoffDate) ? index : -1).filter(index => index !== -1);

  return {
    date: filteredIndices.map(index => BodyCompositionData.date[index]),
    weight: filteredIndices.map(index => BodyCompositionData.weight[index]),
    bodyFat: filteredIndices.map(index => BodyCompositionData.bodyFat[index])
  };
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
  const filteredData = filterBodyCompositionDataByDuration(targetData, durationValue);

  // グラフとテーブルを更新
  updateGraph(filteredData);
  updateBodyCompositionTable(filteredData, granularityValue);
}
document.getElementById("granularity-dropdown").addEventListener("change", handleGranularityChange);

// TODO メソッド名を考えないとなあ。
function handleDurationChange() {
  const granularityValue = document.getElementById("granularity-dropdown").value;
  const durationValue = parseInt(this.value);
  const targetData = granularityValue === "daily" ? dailyData : monthlyData;
  const filteredData = filterBodyCompositionDataByDuration(targetData, durationValue);

  updateGraph(filteredData);
  updateBodyCompositionTable(filteredData, granularityValue);
}
document.getElementById("duration-dropdown").addEventListener("change", handleDurationChange);