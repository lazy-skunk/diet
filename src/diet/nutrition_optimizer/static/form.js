function updateUnitOptionsWithTemplate(select, templateId) {
    const template = document.getElementById(templateId);
    const clonedTemplate = template.content.cloneNode(true);
    select.innerHTML = "";
    select.appendChild(clonedTemplate);
}

function updateUnitOptions(select) {
    const row = select.closest("tr");
    const nutrientSelect = row.querySelector("[name='constraint-nutrient']");
    const unitSelect = row.querySelector("[name='constraint-unit']");

    if (nutrientSelect.value === "energy") {
        updateUnitOptionsWithTemplate(unitSelect, "unit-options-energy");
        unitSelect.disabled = true;
        updateConstraintValueAttributes(row);
        return;
    }

    unitSelect.disabled = false;
    updateUnitOptionsWithTemplate(unitSelect, "unit-options-amount-ratio");
    updateConstraintValueAttributes(row);
}

function removeRowFromTable(button) {
    const row = button.closest("tr");
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

    const unitSelect = template.querySelector("[name='constraint-unit']");
    if (unitSelect) {
        unitSelect.addEventListener("change", () => {
            const row = unitSelect.closest("tr");
            updateConstraintValueAttributes(row);
        });
    }

    const removeButton = template.querySelector("button");
    removeButton.addEventListener("click", () =>
        removeRowFromTable(removeButton),
    );
}

export function appendTemplateToTable(templateId, targetId) {
    const templateElement = document.getElementById(templateId);
    const targetElement = document.getElementById(targetId);
    const clonedTemplate = templateElement.content.cloneNode(true);

    addEventListenersToTemplate(clonedTemplate);
    targetElement.appendChild(clonedTemplate);
}

export function initializeNutrientSelectOnChange() {
    const nutrientSelect = document.querySelector("[name='constraint-nutrient']");
    nutrientSelect.addEventListener("change", () => {
        updateUnitOptions(nutrientSelect);
    });

    const unitSelect = document.querySelector("[name='constraint-unit']");
    unitSelect.addEventListener("change", () => {
        const row = unitSelect.closest("tr");
        updateConstraintValueAttributes(row);
    });
}

function getFoodInformation() {
    const foodInput = document.getElementById("food-inputs");
    const rows = foodInput.querySelectorAll("tr");

    return Array.from(rows).map((row) => {
        const nameInput = row.querySelector("[name='food-name']");
        const gramsPerUnitInput = row.querySelector(
            "[name='food-grams-per-unit']",
        );
        const minimumIntakeInput = row.querySelector(
            "[name='food-minimum-intake']",
        );
        const maximumIntakeInput = row.querySelector(
            "[name='food-maximum-intake']",
        );
        const energyInput = row.querySelector("[name='food-energy']");
        const proteinInput = row.querySelector("[name='food-protein']");
        const fatInput = row.querySelector("[name='food-fat']");
        const carbohydratesInput = row.querySelector(
            "[name='food-carbohydrates']",
        );

        return {
            name: nameInput.value.trim(),
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
    const objectiveInput = document.getElementById("objective-input");
    const row = objectiveInput.querySelector("tr");
    const senseInput = row.querySelector("[name='objective-sense']");
    const nutrientInput = row.querySelector("[name='objective-nutrient']");

    return {
        sense: senseInput.value,
        nutrient: nutrientInput.value,
    };
}

function getConstraints() {
    const constraintInput = document.getElementById("constraint-inputs");
    const rows = constraintInput.querySelectorAll("tr");

    return Array.from(rows).map((row) => {
        const minMaxInput = row.querySelector("[name='constraint-min-max']");
        const nutrientInput = row.querySelector("[name='constraint-nutrient']");
        const unitInput = row.querySelector("[name='constraint-unit']");
        const valueInput = row.querySelector("[name='constraint-value']");

        return {
            minMax: minMaxInput.value,
            nutrient: nutrientInput.value,
            unit: unitInput.value,
            value: Number.parseFloat(valueInput.value),
        };
    });
}

export function buildOptimizePayload() {
    return {
        foodInformation: getFoodInformation(),
        objective: getObjective(),
        constraints: getConstraints(),
    };
}

function updateConstraintValueAttributes(row) {
    const unitSelect = row.querySelector("[name='constraint-unit']");
    const valueInput = row.querySelector("[name='constraint-value']");

    if (unitSelect.value === "ratio") {
        valueInput.max = "100";
        return;
    }

    valueInput.removeAttribute("max");
}

function updateIntakeRangeValidity() {
    const foodInput = document.getElementById("food-inputs");
    const rows = foodInput.querySelectorAll("tr");

    rows.forEach((row) => {
        const minimumIntakeInput = row.querySelector(
            "[name='food-minimum-intake']",
        );
        const maximumIntakeInput = row.querySelector(
            "[name='food-maximum-intake']",
        );
        const minimumIntake = Number.parseInt(minimumIntakeInput.value, 10);
        const maximumIntake = Number.parseInt(maximumIntakeInput.value, 10);

        maximumIntakeInput.setCustomValidity("");
        if (
            Number.isFinite(minimumIntake) &&
            Number.isFinite(maximumIntake) &&
            minimumIntake > maximumIntake
        ) {
            maximumIntakeInput.setCustomValidity(
                "Maximum intake must be greater than or equal to minimum intake.",
            );
        }
    });
}

function getValidationControls() {
    return Array.from(
        document.querySelectorAll(
            "#food-inputs input, #constraint-inputs input",
        ),
    );
}

export function validateOptimizeControls() {
    updateIntakeRangeValidity();

    const firstInvalidControl = getValidationControls().find(
        (control) => !control.checkValidity(),
    );

    if (firstInvalidControl) {
        firstInvalidControl.reportValidity();
        return false;
    }

    return true;
}
