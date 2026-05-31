function drawPFCRatioWithTotalEnergy(pfcRatio, totalNutrientValues) {
    const nutrients = ["protein", "fat", "carbohydrates"];
    const colors = [
        "rgb(255, 128, 128)",
        "rgb(128, 255, 128)",
        "rgb(128, 128, 255)",
    ];
    const pfcData = nutrients.map((nutrient, index) => {
        const capitalizedNutrient =
            nutrient.charAt(0).toUpperCase() + nutrient.slice(1);
        const grams = totalNutrientValues[nutrient];
        const ratio = pfcRatio[nutrient];

        return {
            name: `${capitalizedNutrient} (${grams}g)`,
            y: ratio,
            color: colors[index],
        };
    });

    Highcharts.chart("pfc-ratio-chart", {
        chart: {
            type: "pie",
        },
        title: {
            text: "PFC Ratio",
        },
        tooltip: {
            valueSuffix: "%",
        },
        subtitle: {
            text: `Total Energy: ${totalNutrientValues.energy} kcal`,
        },
        series: [
            {
                name: "Percentage",
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
            text: "Food Intakes",
        },
        xAxis: {
            categories: foodIntakesData.map((item) => item.name),
            title: {
                text: "Food Item",
            },
        },
        yAxis: {
            title: {
                text: "Units",
            },
        },
        series: [
            {
                name: "Food Intakes",
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
    window.alert(`status: ${result.status}
message: ${result.message}`);
}
