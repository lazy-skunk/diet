import { translate } from "../../static/i18n.js";

const pfcNutrients = [
    {
        key: "protein",
        labelKey: "js.protein",
        color: "rgb(255, 128, 128)",
    },
    {
        key: "fat",
        labelKey: "js.fat",
        color: "rgb(128, 255, 128)",
    },
    {
        key: "carbohydrates",
        labelKey: "js.carbohydrates",
        color: "rgb(128, 128, 255)",
    },
];

function drawPfcCompositionRatio(
    pfcCompositionRatio,
    totalNutrientValues,
) {
    const chartData = pfcNutrients.map((nutrient) => {
        const grams = totalNutrientValues[nutrient.key];
        const ratio = pfcCompositionRatio[nutrient.key];

        return {
            name: `${translate(nutrient.labelKey)} (${grams}g)`,
            y: ratio,
            color: nutrient.color,
        };
    });

    Highcharts.chart("pfc-composition-ratio-chart", {
        chart: {
            type: "pie",
        },
        title: {
            text: translate("js.pfc_composition_ratio"),
        },
        tooltip: {
            valueSuffix: "%",
        },
        subtitle: {
            text: `${translate("js.total_energy")}: ${totalNutrientValues.energy} kcal`,
        },
        series: [{
            name: translate("js.percentage"),
            colorByPoint: true,
            data: chartData,
            type: "pie",
        }],
    });
}

function drawFoodIntakeGrams(foodIntakeGrams) {
    const foodIntakeGramsData = Object.keys(foodIntakeGrams).map((food) => ({
        name: food,
        y: foodIntakeGrams[food],
    }));

    Highcharts.chart("food-intake-chart", {
        chart: {
            type: "bar",
        },
        title: {
            text: translate("js.food_intake"),
        },
        xAxis: {
            categories: foodIntakeGramsData.map((item) => item.name),
            title: {
                text: translate("js.food_item"),
            },
        },
        yAxis: {
            title: {
                text: translate("js.intake_grams"),
            },
        },
        series: [
            {
                name: translate("js.food_intake"),
                data: foodIntakeGramsData.map((item) => item.y),
                color: "rgb(128, 128, 255)",
                type: "bar",
            },
        ],
    });
}

function clearCharts() {
    const foodIntakeGramsChart = document.getElementById("food-intake-chart");
    const pfcCompositionRatioChart = document.getElementById(
        "pfc-composition-ratio-chart",
    );

    foodIntakeGramsChart.textContent = "";
    pfcCompositionRatioChart.textContent = "";
}

export function handleOptimizationResult(result) {
    if (result.status === "Optimal") {
        drawPfcCompositionRatio(
            result.pfcCompositionRatio,
            result.totalNutrientValues,
        );
        drawFoodIntakeGrams(result.foodIntakeGrams);
        return;
    }

    clearCharts();
    const translationKey = result.errorCode
        ? `js.${result.errorCode}`
        : "js.optimization_failed";
    const translatedMessage = translate(translationKey);
    const message =
        translatedMessage === translationKey
            ? translate("js.optimization_failed")
            : translatedMessage;
    window.alert(message);
}
