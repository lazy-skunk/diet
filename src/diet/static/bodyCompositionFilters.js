function calculateCutoffDate(durationOption) {
  const cutoffDate = new Date();
  cutoffDate.setHours(0, 0, 0, 0);

  if (durationOption.unit === "months") {
    return new Date(
      cutoffDate.getFullYear(),
      cutoffDate.getMonth() - durationOption.amount + 1,
      1,
    );
  }

  cutoffDate.setDate(cutoffDate.getDate() - durationOption.amount);
  return cutoffDate;
}

function parseDateParts(date) {
  return date.split("-").map(Number);
}

export function getRecordDate(record, granularity) {
  const [year, month, day] = parseDateParts(record.date);
  if (granularity === "monthly") {
    return new Date(year, month, 0);
  }
  return new Date(year, month - 1, day);
}

export function filterDataByDuration(records, durationOption, granularity) {
  const cutoffDate = calculateCutoffDate(durationOption);
  return records.filter(
    (record) => getRecordDate(record, granularity) >= cutoffDate,
  );
}

export function sortRecordsByDateDesc(records, granularity) {
  return [...records].sort(
    (a, b) => getRecordDate(b, granularity) - getRecordDate(a, granularity),
  );
}
