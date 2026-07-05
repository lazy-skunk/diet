import { getGranularityConfig } from "./bodyCompositionConfig.js";
import { sortRecordsByDateDesc } from "./bodyCompositionFilters.js";
import { translate } from "./i18n.js";

function formatTableValue(value) {
  return value === null || value === undefined ? "-" : value;
}

function getTableHeaders(config) {
  const headers = [translate("js.date"), config.weightHeader, config.bodyFatHeader];
  if (config.weightChangeRateHeader) {
    headers.push(config.weightChangeRateHeader);
  }
  return headers;
}

function createCell(tagName, text) {
  const cell = document.createElement(tagName);
  cell.textContent = text;
  return cell;
}

function createTableHead(config) {
  const thead = document.createElement("thead");
  const row = document.createElement("tr");

  for (const header of getTableHeaders(config)) {
    row.appendChild(createCell("th", header));
  }

  thead.appendChild(row);
  return thead;
}

function createEmptyTableRow(config) {
  const row = document.createElement("tr");
  const cell = createCell("td", translate("js.no_data"));
  cell.colSpan = getTableHeaders(config).length;
  row.appendChild(cell);
  return row;
}

function createRecordTableRow(record, config) {
  const row = document.createElement("tr");
  row.appendChild(createCell("td", record.date));
  row.appendChild(createCell("td", formatTableValue(record.weight)));
  row.appendChild(createCell("td", formatTableValue(record.bodyFat)));

  if (config.weightChangeRateHeader) {
    row.appendChild(createCell("td", formatTableValue(record.weightChangeRate)));
  }

  return row;
}

function createTableBody(records, config, granularity) {
  const tbody = document.createElement("tbody");

  if (records.length === 0) {
    tbody.appendChild(createEmptyTableRow(config));
    return tbody;
  }

  for (const record of sortRecordsByDateDesc(records, granularity)) {
    tbody.appendChild(createRecordTableRow(record, config));
  }

  return tbody;
}

export function updateTable(tableElement, records, granularity) {
  const config = getGranularityConfig(granularity);
  tableElement.replaceChildren(
    createTableHead(config),
    createTableBody(records, config, granularity),
  );
}

