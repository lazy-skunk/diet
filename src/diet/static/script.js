import { fetchBodyCompositionData } from "./bodyCompositionApi.js";
import { updateChart } from "./bodyCompositionChart.js";
import {
  defaultGranularity,
  getGranularityConfig,
  granularityConfig,
} from "./bodyCompositionConfig.js";
import { filterDataByDuration } from "./bodyCompositionFilters.js";
import { updateTable } from "./bodyCompositionTable.js";

const state = {
  daily: [],
  monthly: [],
};

function getDashboardElement() {
  return document.getElementById("body-composition-dashboard");
}

function getApiEndpoint() {
  return getDashboardElement().dataset.apiEndpoint;
}

function getGranularityDropdown() {
  return document.getElementById("granularity-dropdown");
}

function getDurationDropdown() {
  return document.getElementById("duration-dropdown");
}

function getChartCanvas() {
  return document.getElementById("bodyCompositionGraph");
}

function getTable() {
  return document.getElementById("body-composition-table");
}

function appendOption(selectElement, value, label, selectedValue) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = label;
  option.selected = value === selectedValue;
  selectElement.appendChild(option);
}

async function loadBodyCompositionData() {
  try {
    const bodyCompositionData = await fetchBodyCompositionData(
      getApiEndpoint(),
    );
    state.daily = bodyCompositionData.daily;
    state.monthly = bodyCompositionData.monthly;
  } catch (error) {
    console.error(error);
    state.daily = [];
    state.monthly = [];
  }
}

function getGranularityValue() {
  return getGranularityDropdown().value;
}

function getRecords(granularity) {
  const config = getGranularityConfig(granularity);
  return state[config.dataKey];
}

function getDurationOption(granularity) {
  const config = getGranularityConfig(granularity);
  const selectedValue = getDurationDropdown().value;
  return (
    config.durationOptions.find((option) => option.value === selectedValue) ||
    config.durationOptions.find(
      (option) => option.value === config.defaultDuration,
    )
  );
}

function updateGranularityOptions() {
  const granularityDropdown = getGranularityDropdown();
  granularityDropdown.replaceChildren();

  for (const [value, config] of Object.entries(granularityConfig)) {
    appendOption(granularityDropdown, value, config.label, defaultGranularity);
  }
}

function updateDurationOptions(granularity) {
  const config = getGranularityConfig(granularity);
  const durationDropdown = getDurationDropdown();
  durationDropdown.replaceChildren();

  for (const option of config.durationOptions) {
    appendOption(
      durationDropdown,
      option.value,
      option.label,
      config.defaultDuration,
    );
  }
}

function renderCurrentSelection() {
  const granularity = getGranularityValue();
  const durationOption = getDurationOption(granularity);
  const records = getRecords(granularity);
  const filteredRecords = filterDataByDuration(
    records,
    durationOption,
    granularity,
  );
  updateChart(getChartCanvas(), filteredRecords, granularity);
  updateTable(getTable(), filteredRecords, granularity);
}

async function loadDataAndRender() {
  await loadBodyCompositionData();
  renderCurrentSelection();
}

function handleGranularityChange() {
  updateDurationOptions(getGranularityValue());
  renderCurrentSelection();
}

function handleDurationChange() {
  renderCurrentSelection();
}

function initializeBodyCompositionVisualization() {
  updateGranularityOptions();
  updateDurationOptions(getGranularityValue());
  getGranularityDropdown().addEventListener("change", handleGranularityChange);
  getDurationDropdown().addEventListener("change", handleDurationChange);
  loadDataAndRender();
}

window.addEventListener("load", initializeBodyCompositionVisualization);
