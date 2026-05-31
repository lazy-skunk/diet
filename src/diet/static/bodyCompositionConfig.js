const durationOptions = {
  sevenDays: { value: "7d", label: "7 Days", unit: "days", amount: 7 },
  thirtyDays: { value: "30d", label: "30 Days", unit: "days", amount: 30 },
  ninetyDays: { value: "90d", label: "90 Days", unit: "days", amount: 90 },
  oneHundredEightyDays: {
    value: "180d",
    label: "180 Days",
    unit: "days",
    amount: 180,
  },
  sixMonths: { value: "6m", label: "6 Months", unit: "months", amount: 6 },
  oneYear: { value: "12m", label: "1 Year", unit: "months", amount: 12 },
  threeYears: {
    value: "36m",
    label: "3 Years",
    unit: "months",
    amount: 36,
  },
};

export const defaultGranularity = "daily";

export const granularityConfig = {
  daily: {
    label: "Daily",
    dataKey: "daily",
    defaultDuration: "30d",
    durationOptions: [
      durationOptions.sevenDays,
      durationOptions.thirtyDays,
      durationOptions.ninetyDays,
      durationOptions.oneHundredEightyDays,
    ],
    weightLabel: "Weight",
    bodyFatLabel: "Body Fat Percentage",
    weightHeader: "Weight (kg)",
    bodyFatHeader: "Body Fat Percentage (%)",
  },
  monthly: {
    label: "Monthly",
    dataKey: "monthly",
    defaultDuration: "12m",
    durationOptions: [
      durationOptions.sixMonths,
      durationOptions.oneYear,
      durationOptions.threeYears,
    ],
    weightLabel: "Average Weight",
    bodyFatLabel: "Average Body Fat Percentage",
    weightHeader: "Average Weight (kg)",
    bodyFatHeader: "Average Body Fat Percentage (%)",
    weightChangeRateHeader: "Change Rate from Last Month (%)",
  },
};

export function getGranularityConfig(granularity) {
  return granularityConfig[granularity] || granularityConfig[defaultGranularity];
}
