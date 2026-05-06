import {
    getClosestTableRowElementOrThrow,
    getElementByIdOrThrow,
    getElementByQuerySelectorOrThrow,
    getElementsByQuerySelectorAllOrThrow,
} from "./nutritionOptimizerDomUtilities.js";

function updateUnitOptionsWithTemplate(select, templateId) {
    const template = getElementByIdOrThrow(templateId);
    const clonedTemplate = template.content.cloneNode(true);
    select.innerHTML = "";
    select.appendChild(clonedTemplate);
}

export function updateUnitOptions(select) {
    const row = getClosestTableRowElementOrThrow(select);
    const nutrientSelect = getElementByQuerySelectorOrThrow(
        row,
        "[name='constraint-nutrient']",
    );
    const unitSelect = getElementByQuerySelectorOrThrow(
        row,
        "[name='constraint-unit']",
    );

    if (nutrientSelect.value === "energy") {
        updateUnitOptionsWithTemplate(unitSelect, "unit-options-energy");
        unitSelect.disabled = true;
        return;
    }

    unitSelect.disabled = false;
    updateUnitOptionsWithTemplate(unitSelect, "unit-options-amount-ratio");
}

function removeRowFromTable(button) {
    const row = getClosestTableRowElementOrThrow(button);
    row.remove();
}

function addEventListenersToTemplate(template) {
    const nutrientSelect = template.querySelector(
        "[name='constraint-nutrient']",
    );
    if (nutrientSelect) {
        nutrientSelect.addEventListener("change", () =>
            updateUnitOptions(nutrientSelect),
        );
    }

    const removeButton = getElementByQuerySelectorOrThrow(template, "button");
    removeButton.addEventListener("click", () =>
        removeRowFromTable(removeButton),
    );
}

export function appendTemplateToTable(templateId, targetId) {
    const templateElement = getElementByIdOrThrow(templateId);
    const targetElement = getElementByIdOrThrow(targetId);
    const clonedTemplate = templateElement.content.cloneNode(true);

    addEventListenersToTemplate(clonedTemplate);
    targetElement.appendChild(clonedTemplate);
}

export function initializeNutrientSelectOnChange() {
    const nutrientSelect = getElementByQuerySelectorOrThrow(
        document,
        "[name='constraint-nutrient']",
    );
    nutrientSelect.addEventListener("change", () => {
        updateUnitOptions(nutrientSelect);
    });
}

function getFoodInformation() {
    const foodInput = getElementByIdOrThrow("food-inputs");
    const rows = getElementsByQuerySelectorAllOrThrow(foodInput, "tr");

    return Array.from(rows).map((row) => {
        const nameInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-name']",
        );
        const gramsPerUnitInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-grams-per-unit']",
        );
        const minimumIntakeInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-minimum-intake']",
        );
        const maximumIntakeInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-maximum-intake']",
        );
        const energyInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-energy']",
        );
        const proteinInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-protein']",
        );
        const fatInput = getElementByQuerySelectorOrThrow(row, "[name='food-fat']");
        const carbohydratesInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='food-carbohydrates']",
        );

        return {
            name: nameInput.value,
            gramsPerUnit: Number.parseInt(gramsPerUnitInput.value, 10),
            minimumIntake: Number.parseInt(minimumIntakeInput.value, 10),
            maximumIntake: Number.parseInt(maximumIntakeInput.value, 10),
            energy: Number.parseFloat(energyInput.value),
            protein: Number.parseFloat(proteinInput.value),
            fat: Number.parseFloat(fatInput.value),
            carbohydrates: Number.parseFloat(carbohydratesInput.value),
        };
    });
}

function getObjective() {
    const objectiveInput = getElementByIdOrThrow("objective-input");
    const row = getElementByQuerySelectorOrThrow(objectiveInput, "tr");
    const senseInput = getElementByQuerySelectorOrThrow(
        row,
        "[name='objective-sense']",
    );
    const nutrientInput = getElementByQuerySelectorOrThrow(
        row,
        "[name='objective-nutrient']",
    );

    return {
        sense: senseInput.value,
        nutrient: nutrientInput.value,
    };
}

function getConstraints() {
    const constraintInput = getElementByIdOrThrow("constraint-inputs");
    const rows = getElementsByQuerySelectorAllOrThrow(constraintInput, "tr");

    return Array.from(rows).map((row) => {
        const minMaxInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='constraint-min-max']",
        );
        const nutrientInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='constraint-nutrient']",
        );
        const unitInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='constraint-unit']",
        );
        const valueInput = getElementByQuerySelectorOrThrow(
            row,
            "[name='constraint-value']",
        );

        return {
            minMax: minMaxInput.value,
            nutrient: nutrientInput.value,
            unit: unitInput.value,
            value: Number.parseFloat(valueInput.value),
        };
    });
}

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
    const foodIntakesChart = getElementByIdOrThrow("food-intakes-chart");
    const pfcRatioChart = getElementByIdOrThrow("pfc-ratio-chart");

    foodIntakesChart.textContent = "";
    pfcRatioChart.textContent = "";
}

function getCsrfToken() {
    const csrfTokenMeta = document.querySelector("meta[name='csrf-token']");
    if (!(csrfTokenMeta instanceof HTMLMetaElement)) {
        throw new Error("CSRF token is missing");
    }

    return csrfTokenMeta.content;
}

function handleOptimizationResult(result) {
    if (result.status === "Optimal") {
        drawPFCRatioWithTotalEnergy(
            result.pfcRatio,
            result.totalNutrientValues,
        );
        drawFoodIntakes(result.foodIntakes);
        return;
    }

    clearCharts();
    window.alert(`status: ${result.status}\nmessage: ${result.message}`);
}

export async function optimize() {
    try {
        const optimizeButton = getElementByIdOrThrow("optimize");
        const response = await fetch(optimizeButton.dataset.optimizeUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({
                foodInformation: getFoodInformation(),
                objective: getObjective(),
                constraints: getConstraints(),
            }),
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        handleOptimizationResult(result);
    } catch (error) {
        if (error instanceof Error) {
            window.alert(error.message);
        }
    }
}
