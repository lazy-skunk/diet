import { translate } from "./i18n.js";

const durationOptions = {
  sevenDays: { value: "7d", label: translate("js.7_days"), unit: "days", amount: 7 },
  thirtyDays: { value: "30d", label: translate("js.30_days"), unit: "days", amount: 30 },
  ninetyDays: { value: "90d", label: translate("js.90_days"), unit: "days", amount: 90 },
  oneHundredEightyDays: {
    value: "180d",
    label: translate("js.180_days"),
    unit: "days",
    amount: 180,
  },
  sixMonths: { value: "6m", label: translate("js.6_months"), unit: "months", amount: 6 },
  oneYear: { value: "12m", label: translate("js.1_year"), unit: "months", amount: 12 },
  threeYears: {
    value: "36m",
    label: translate("js.3_years"),
    unit: "months",
    amount: 36,
  },
};

export const defaultGranularity = "daily";

export const granularityConfig = {
  daily: {
    label: translate("js.daily"),
    dataKey: "daily",
    defaultDuration: "30d",
    durationOptions: [
      durationOptions.sevenDays,
      durationOptions.thirtyDays,
      durationOptions.ninetyDays,
      durationOptions.oneHundredEightyDays,
    ],
    weightLabel: translate("js.weight"),
    bodyFatLabel: translate("js.body_fat_percentage"),
    weightHeader: translate("js.weight_kg"),
    bodyFatHeader: translate("js.body_fat_percentage_percent"),
  },
  monthly: {
    label: translate("js.monthly"),
    dataKey: "monthly",
    defaultDuration: "12m",
    durationOptions: [
      durationOptions.sixMonths,
      durationOptions.oneYear,
      durationOptions.threeYears,
    ],
    weightLabel: translate("js.average_weight"),
    bodyFatLabel: translate("js.average_body_fat_percentage"),
    weightHeader: translate("js.average_weight_kg"),
    bodyFatHeader: translate("js.average_body_fat_percentage_percent"),
    weightChangeRateHeader: translate("js.change_rate_last_month"),
  },
};

export function getGranularityConfig(granularity) {
  return granularityConfig[granularity] || granularityConfig[defaultGranularity];
}

