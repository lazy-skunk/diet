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

function drawPFCRatioWithTotalEnergy(pfcRatio, totalNutrientValues) {
    const pfcData = pfcNutrients.map((nutrient) => {
        const grams = totalNutrientValues[nutrient.key];
        const ratio = pfcRatio[nutrient.key];

        return {
            name: `${translate(nutrient.labelKey)} (${grams}g)`,
            y: ratio,
            color: nutrient.color,
        };
    });

    Highcharts.chart("pfc-ratio-chart", {
        chart: {
            type: "pie",
        },
        title: {
            text: translate("js.pfc_ratio"),
        },
        tooltip: {
            valueSuffix: "%",
        },
        subtitle: {
            text: `${translate("js.total_energy")}: ${totalNutrientValues.energy} kcal`,
        },
        series: [
            {
                name: translate("js.percentage"),
                colorByPoint: true,
                data: pfcData,
            },
        ],
    });
}

function drawFoodIntakes(foodIntakes) {
    const foodIntakesData = Object.keys(foodIntakes).map((food) => ({
        name: food,
        y: foodIntakes[food],
    }));

    Highcharts.chart("food-intakes-chart", {
        chart: {
            type: "bar",
        },
        title: {
            text: translate("js.food_intakes"),
        },
        xAxis: {
            categories: foodIntakesData.map((item) => item.name),
            title: {
                text: translate("js.food_item"),
            },
        },
        yAxis: {
            title: {
                text: translate("js.units"),
            },
        },
        series: [
            {
                name: translate("js.food_intakes"),
                data: foodIntakesData.map((item) => item.y),
                color: "rgb(128, 128, 255)",
                type: "bar",
            },
        ],
    });
}

function clearCharts() {
    const foodIntakesChart = document.getElementById("food-intakes-chart");
    const pfcRatioChart = document.getElementById("pfc-ratio-chart");

    foodIntakesChart.textContent = "";
    pfcRatioChart.textContent = "";
}

export function handleOptimizationResult(result) {
    if (result.status === "Optimal") {
        drawPFCRatioWithTotalEnergy(
            result.pfcRatio,
            result.totalNutrientValues,
        );
        drawFoodIntakes(result.foodIntakes);
        return;
    }

    clearCharts();
    window.alert(`${translate("js.status")}: ${result.status}
${translate("js.message")}: ${result.message}`);
}

