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

async function initializePage() {
  await fetchData();
  const durationValue = parseInt(document.getElementById("duration-dropdown").value);
  console.log(durationValue)
  const filteredData = filterDataByDuration(dailyData, durationValue);
  console.log(filteredData)
  createGraph(filteredData);
};

async function fetchData() {
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

function createGraph(data) {
  const ctx = document.getElementById("bodyCompositionGraph").getContext("2d");
  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.date,
      datasets: [
        {
          label: "体重",
          data: data.weight,
          yAxisID: "y",
          spanGaps: true,
          pointRadius: 0,
          pointHoverRadius: 0
        },
        {
          label: "体脂肪率",
          data: data.bodyFat,
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

window.onload = initializePage();

function updateGraph(data) {
  chartInstance.data.labels = data.date;
  chartInstance.data.datasets[0].data = data.weight;
  chartInstance.data.datasets[1].data = data.bodyFat;
  chartInstance.update();
}

// ここから下は作成していく。
function filterDataByDuration(data, days) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const filteredIndices = data.date.map((d, index) => (new Date(d) >= cutoffDate) ? index : -1).filter(index => index !== -1);

  return {
    date: filteredIndices.map(index => data.date[index]),
    weight: filteredIndices.map(index => data.weight[index]),
    bodyFat: filteredIndices.map(index => data.bodyFat[index])
  };
}


// 表示粒度を変更した場合の処理
document.getElementById("granularity-dropdown").addEventListener("change", function () {
  const granularity = this.value;
  let options = [
    { value: "7", label: "1週間" },
    { value: "30", label: "1か月" },
    { value: "90", label: "3か月" },
    { value: "180", label: "半年" },
    { value: "365", label: "1年" },
    { value: "1095", label: "3年" }
  ];

  if (granularity === "monthly") {
    options = options.filter(opt => opt.value !== "7");
  }

  let defaultSelectedValue = granularity === "monthly" ? "365" : "30";

  const durationDropdown = document.getElementById("duration-dropdown");
  durationDropdown.innerHTML = options.map(opt => {
    let selected = opt.value === defaultSelectedValue ? ' selected' : '';
    return `<option value="${opt.value}"${selected}>${opt.label}</option>`;
  }).join('');

  const durationValue = parseInt(durationDropdown.value);

  const filteredData = filterDataByDuration(allData, durationValue);
  updateGraph(filteredData);
});

// 表示期間を変更した場合の処理
document.getElementById("duration-dropdown").addEventListener("change", function () {
  const granularityValue = document.getElementById("granularity-dropdown").value;
  const durationValue = parseInt(this.value);
  const targetData = granularityValue === "daily" ? dailyData : monthlyData;

  const filteredData = filterDataByDuration(targetData, durationValue);

  updateGraph(filteredData);
});




/*
function updateTable(dates, weightData, bodyFatData, weightChangeRate, granularity) {
  const tableContainer = document.getElementById("body-composition-table");

  let weightHeader = granularity === "monthly" ? "平均体重 (kg)" : "体重 (kg)";
  let bodyFatHeader = granularity === "monthly" ? "平均体脂肪率 (%)" : "体脂肪率 (%)";

  let tableHtml = `
  <thead>
  <tr>
  <th>日付</th>
  <th>${weightHeader}</th>
  <th>${bodyFatHeader}</th>
  `;

  // 月別の表示の場合だけ、体重変化率を追加
  if (granularity === "monthly") {
    tableHtml += `<th>体重変化率 (%)</th>`;
  }

  tableHtml += `</tr></thead><tbody>`;

  const indices = Array.from({ length: dates.length }, (_, i) => i);
  indices.sort((a, b) => {
    const dateA = new Date(dates[a]);
    const dateB = new Date(dates[b]);
    return dateB - dateA;
  });

  for (const i of indices) {
    tableHtml += `<tr>
    <td>${dates[i]}</td>
    <td>${weightData[i].toFixed(2)}</td>
    <td>${bodyFatData[i] ? bodyFatData[i].toFixed(2) : "N/A"}</td>`;
    if (granularity === "monthly" && weightChangeRate[i]) {
      tableHtml += `<td>${weightChangeRate[i].toFixed(2)}</td>`;
    }
    tableHtml += `</tr>`;
  }

  tableHtml += `</tbody>`;
  tableContainer.innerHTML = tableHtml;
}

function filterDataByDays(data, days) {
  const now = new Date();
  const cutoffDate = new Date();
  cutoffDate.setDate(now.getDate() - days);
  return data.filter(item => new Date(item.date) > cutoffDate);
}

function average(arr) {
  if (arr.length === 0) return null;
  const sum = arr.reduce((acc, val) => acc + val, 0);
  return parseFloat((sum / arr.length).toFixed(2));
}

function processMonthlyData(data) {
  const monthlyData = {
    dates: [],
    weight_data: [],
    body_fat_data: [],
    weight_change_rate: []  // 体重変化率のデータを保持する配列
  };
  
  let tempWeights = [];
  let tempBodyFats = [];
  let currentMonth = new Date(data.dates[0]).getMonth();
  let currentYear = new Date(data.dates[0]).getFullYear();
  
  for (let i = 0; i < data.dates.length; i++) {
    const date = new Date(data.dates[i]);
    const month = date.getMonth();
  const year = date.getFullYear();
  
  if (month !== currentMonth || i === data.dates.length - 1) {
    if (i === data.dates.length - 1 && month === currentMonth) {
      tempWeights.push(data.weight_data[i]);
      tempBodyFats.push(data.body_fat_data[i]);
    }
    
    monthlyData.dates.push(`${currentYear}-${String(currentMonth + 1).padStart(2, '0')}`);
    monthlyData.weight_data.push(average(tempWeights));
    monthlyData.body_fat_data.push(average(tempBodyFats));
    
    // 体重変化率の計算
    if (monthlyData.weight_data.length > 1) {
      const prevWeight = monthlyData.weight_data[monthlyData.weight_data.length - 2];
      const currentWeight = average(tempWeights);
      const changeRate = ((currentWeight - prevWeight) / prevWeight) * 100;
      monthlyData.weight_change_rate.push(parseFloat(changeRate.toFixed(2))); // 小数点第2位まで四捨五入
    } else {
      // 最初のデータポイントでは変化率が計算できないのでnullを挿入
      monthlyData.weight_change_rate.push(null);
    }
    
    tempWeights = [];
    tempBodyFats = [];
    currentMonth = month;
    currentYear = year;
  }

  if (i !== data.dates.length - 1 || month !== currentMonth) {
    tempWeights.push(data.weight_data[i]);
    tempBodyFats.push(data.body_fat_data[i]);
  }
}
 
return monthlyData;
}
*/