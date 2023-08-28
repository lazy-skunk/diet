/** 
 * 全体のデータを保持するオブジェクト
 * @type {Object} 
 */
let allData = {};

/**
 * グラフのインスタンスを保持する変数
 * @type {Chart|null}
 */
let chartInstance = null;

/**
 * グラフを作成または更新します。
 * @param {string[]} labels - グラフのX軸のラベル（日付）
 * @param {number[]} weightData - 体重のデータ配列
 * @param {number[]} bodyFatData - 体脂肪率のデータ配列
 */
function createOrUpdateGraph(labels, weightData, bodyFatData) {
  const ctx = document.getElementById("bodyCompositionGraph").getContext("2d");

  if (chartInstance) {
    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].data = weightData;
    chartInstance.data.datasets[1].data = bodyFatData;
    chartInstance.update();
  } else {
    chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "体重",
            data: weightData,
            borderColor: "rgba(255, 99, 132, 1)",
            yAxisID: "y",
            spanGaps: true
          },
          {
            label: "体脂肪率",
            data: bodyFatData,
            borderColor: "rgba(54, 162, 235, 1)",
            yAxisID: "y1",
            spanGaps: true
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
}

/**
 * 表を更新します。
 * @param {string[]} dates - 日付の配列
 * @param {number[]} weightData - 体重のデータ配列
 * @param {number[]} bodyFatData - 体脂肪率のデータ配列
 */
function updateTable(dates, weightData, bodyFatData) {
  const tableContainer = document.getElementById("body-composition-table");
  let tableHtml = '<thead><tr><th>日付</th><th>体重 (kg)</th><th>体脂肪率 (%)</th></tr></thead><tbody>';

  const indices = Array.from({ length: dates.length }, (_, i) => i);
  indices.sort((a, b) => {
    const dateA = new Date(dates[a]);
    const dateB = new Date(dates[b]);
    return dateB - dateA;
  });

  for (const i of indices) {
    tableHtml += `<tr><td>${dates[i]}</td><td>${weightData[i]}</td><td>${bodyFatData[i] || '-'}</td></tr>`;
  }

  tableHtml += '</tbody>';
  tableContainer.innerHTML = tableHtml;
}

/**
 * 指定した期間に基づいてデータをフィルタリングします。
 * @deprecated この関数は古い方式でのフィルタリングのため、代わりにfilterDataByDaysを使用してください。
 * @param {Object} data - フィルタリングする前のデータ
 * @param {string} duration - 表示期間（"all"か日数）
 * @returns {Object} フィルタリングされたデータ
 */
function filterDataByDuration(data, duration) {
  let filteredData;

  if (duration === "all") {
    filteredData = data;
  } else {
    const durationInt = parseInt(duration, 10);
    filteredData = {
      dates: data.dates.slice(-durationInt),
      weight_data: data.weight_data.slice(-durationInt),
      body_fat_data: data.body_fat_data.slice(-durationInt)
    };
  }

  return filteredData;  // ここでは日付をソートせず、そのまま返す
}

/**
 * 指定した日数に基づいてデータをフィルタリングします。
 * @param {Object} data - フィルタリングする前のデータ
 * @param {number|string} days - フィルタリングする日数（"all"か日数）
 * @returns {Object} フィルタリングされたデータ
 */
function filterDataByDays(data, days) {
  const now = new Date();
  const cutoff = new Date();
  cutoff.setDate(now.getDate() - days);

  const filteredData = {
    weight_data: [],
    body_fat_data: [],
    dates: []
  };

  for (let i = 0; i < data.dates.length; i++) {
    const date = new Date(data.dates[i]);
    if (days === "all" || date >= cutoff) {
      filteredData.weight_data.push(data.weight_data[i]);
      filteredData.body_fat_data.push(data.body_fat_data[i]);
      filteredData.dates.push(data.dates[i]);
    }
  }
  return filteredData;
}

// ドロップダウンメニューの変更を監視し、データをフィルタリングしてグラフと表を更新
document.getElementById("duration-dropdown").addEventListener("change", function () {
  const days = this.value;
  const filteredData = filterDataByDays(allData, days === "all" ? days : parseInt(days));
  createOrUpdateGraph(filteredData.dates, filteredData.weight_data, filteredData.body_fat_data);
  updateTable(filteredData.dates, filteredData.weight_data, filteredData.body_fat_data);
});

// サーバーからデータを取得し、グラフと表を初期化
fetch("/get_body_composition_data")
  .then((response) => response.json())
  .then((data) => {
    allData = data;
    const initialData = filterDataByDays(allData, 30);

    // グラフとテーブルを更新
    createOrUpdateGraph(initialData.dates, initialData.weight_data, initialData.body_fat_data);
    updateTable(initialData.dates, initialData.weight_data, initialData.body_fat_data);
  });