import { translate } from "../../static/i18n.js";
import { addFoodPickerTrigger } from "./foodCatalog.js";

let nutrientDefinitions = [];

function parseEmbeddedJson(elementId) {
    const element = document.getElementById(elementId);
    if (!(element instanceof HTMLScriptElement) || !element.textContent) {
        throw new Error(`Missing embedded JSON: ${elementId}`);
    }

    return JSON.parse(element.textContent);
}

function initializeNutrientDefinitions() {
    nutrientDefinitions = parseEmbeddedJson("nutrient-definition-data");
}

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
    updateUnitOptionsWithTemplate(
        unitSelect,
        "unit-options-amount-pfc-ratio",
    );
    updateConstraintValueAttributes(row);
}

function removeRowFromTable(button) {
    const row = button.closest("tr");
    row.remove();
}

function formatNutrientLabel(definition) {
    const label = definition.name;
    if (!definition.displayUnit) {
        return label;
    }

    return `${label} (${definition.displayUnit})`;
}

function clearGeneratedColumns(selector) {
    document.querySelectorAll(selector).forEach((element) => element.remove());
}

function createHeaderCell(definition, attributeName) {
    const header = document.createElement("th");
    header.scope = "col";
    header.dataset[attributeName] = definition.identifier;
    header.textContent = formatNutrientLabel(definition);
    header.title = definition.name;
    return header;
}

function nutrientInputName(definition) {
    return `food-nutrient-${definition.key}`;
}

function getManualNutrientValues(row) {
    return Object.fromEntries(
        nutrientDefinitions.map((definition) => {
            const input = row.querySelector(
                `[name='${nutrientInputName(definition)}']`,
            );
            return [definition.identifier, input?.value || ""];
        }),
    );
}

function createFoodNutrientCell(definition, existingValues) {
    const cell = document.createElement("td");
    const input = document.createElement("input");
    cell.dataset.generatedFoodCell = definition.identifier;
    cell.title = definition.name;
    input.type = "number";
    input.className = "form-control";
    input.name = nutrientInputName(definition);
    input.min = "0";
    input.step = "any";
    input.required = true;
    input.value = existingValues[definition.identifier] ?? "";

    cell.appendChild(input);
    return cell;
}

function renderFoodTableNutrientColumns() {
    const headerRow = document.querySelector("#food-table thead tr");
    const minimumHeader = headerRow.querySelector(
        "[data-static-column='minimum']",
    );

    clearGeneratedColumns("[data-generated-food-column]");
    nutrientDefinitions.forEach((definition) => {
        headerRow.insertBefore(
            createHeaderCell(definition, "generatedFoodColumn"),
            minimumHeader,
        );
    });

    document.querySelectorAll("#food-inputs tr").forEach((row) => {
        const existingValues = getManualNutrientValues(row);
        const minimumCell = row.querySelector(
            "[data-static-cell='minimum']",
        );

        row.querySelectorAll("[data-generated-food-cell]").forEach((cell) =>
            cell.remove(),
        );
        nutrientDefinitions.forEach((definition) => {
            row.insertBefore(
                createFoodNutrientCell(definition, existingValues),
                minimumCell,
            );
        });
    });
}

export function fillFoodRow(row, food) {
    const foodNameInput = row.querySelector("[name='food-name']");

    foodNameInput.value = food.name;
    foodNameInput.setCustomValidity("");
    nutrientDefinitions.forEach((definition) => {
        const input = row.querySelector(
            `[name='${nutrientInputName(definition)}']`,
        );
        input.value = food.nutrientValues[definition.identifier] ?? "";
    });
}

function updateFoodActionButtons() {
    const rows = document.querySelectorAll("#food-inputs tr");
    rows.forEach((row) => {
        const removeButton = row.querySelector("[data-remove-food-row]");
        if (removeButton) {
            removeButton.disabled = rows.length === 1;
        }
    });
}

function addFoodRowAfter(button) {
    const templateElement = document.getElementById("food-template");
    const clonedTemplate = templateElement.content.cloneNode(true);
    const currentRow = button.closest("tr");

    addEventListenersToTemplate(clonedTemplate);
    currentRow.after(clonedTemplate);
    renderFoodTableNutrientColumns();
    updateFoodActionButtons();
}

function removeFoodRow(button) {
    const rows = document.querySelectorAll("#food-inputs tr");
    if (rows.length === 1) {
        return;
    }

    removeRowFromTable(button);
    updateFoodActionButtons();
}

function addFoodActionTriggers(root) {
    const addButton = root.querySelector("[data-add-food-row]");
    if (addButton) {
        addButton.addEventListener("click", () => addFoodRowAfter(addButton));
    }

    const removeButton = root.querySelector("[data-remove-food-row]");
    if (removeButton) {
        removeButton.addEventListener("click", () => removeFoodRow(removeButton));
    }
}

function updateConstraintActionButtons() {
    const rows = document.querySelectorAll("#constraint-inputs tr");
    rows.forEach((row) => {
        const removeButton = row.querySelector("[data-remove-constraint-row]");
        if (removeButton) {
            removeButton.disabled = rows.length === 1;
        }
    });
}

function addConstraintRowAfter(button) {
    const templateElement = document.getElementById("constraint-template");
    const clonedTemplate = templateElement.content.cloneNode(true);
    const currentRow = button.closest("tr");

    addEventListenersToTemplate(clonedTemplate);
    currentRow.after(clonedTemplate);
    updateConstraintActionButtons();
}

function removeConstraintRow(button) {
    const rows = document.querySelectorAll("#constraint-inputs tr");
    if (rows.length === 1) {
        return;
    }

    removeRowFromTable(button);
    updateConstraintActionButtons();
}

function addConstraintActionTriggers(root) {
    const addButton = root.querySelector("[data-add-constraint-row]");
    if (addButton) {
        addButton.addEventListener("click", () =>
            addConstraintRowAfter(addButton),
        );
    }

    const removeButton = root.querySelector("[data-remove-constraint-row]");
    if (removeButton) {
        removeButton.addEventListener("click", () =>
            removeConstraintRow(removeButton),
        );
    }
}

function addEventListenersToTemplate(template) {
    addFoodPickerTrigger(template);
    addFoodActionTriggers(template);
    addConstraintActionTriggers(template);

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
}

export function initializeFoodRows() {
    document.querySelectorAll("#food-inputs tr").forEach((row) => {
        addEventListenersToTemplate(row);
    });
    updateFoodActionButtons();
}

export function initializeConstraintRows() {
    document.querySelectorAll("#constraint-inputs tr").forEach((row) => {
        addEventListenersToTemplate(row);
    });
    updateConstraintActionButtons();
}

export function initializeNutrientColumns() {
    initializeNutrientDefinitions();
    renderFoodTableNutrientColumns();
    return nutrientDefinitions;
}

function getFoodSelections() {
    const foodInput = document.getElementById("food-inputs");
    const rows = foodInput.querySelectorAll("tr");

    return Array.from(rows).map((row) => {
        const minimumIntakeGramsInput = row.querySelector(
            "[name='food-minimum-intake-grams']",
        );
        const maximumIntakeGramsInput = row.querySelector(
            "[name='food-maximum-intake-grams']",
        );

        const selection = {
            minimumIntakeGrams: minimumIntakeGramsInput.valueAsNumber,
            maximumIntakeGrams: maximumIntakeGramsInput.valueAsNumber,
        };

        const manualNutrients = Object.fromEntries(
            nutrientDefinitions.map((definition) => {
                const input = row.querySelector(
                    `[name='${nutrientInputName(definition)}']`,
                );
                return [
                    definition.key,
                    Number.parseFloat(input.value),
                ];
            }),
        );

        return {
            ...selection,
            foodName: row.querySelector("[name='food-name']").value.trim(),
            ...manualNutrients,
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
        foodSelections: getFoodSelections(),
        objective: getObjective(),
        constraints: getConstraints(),
    };
}

function updateConstraintValueAttributes(row) {
    const unitSelect = row.querySelector("[name='constraint-unit']");
    const valueInput = row.querySelector("[name='constraint-value']");

    if (unitSelect.value === "pfc_ratio") {
        valueInput.max = "100";
        return;
    }

    valueInput.removeAttribute("max");
}

function updateFoodValidity() {
    const foodRows = document.querySelectorAll("#food-inputs tr");
    const foodNames = new Set();

    foodRows.forEach((row) => {
        const foodNameInput = row.querySelector("[name='food-name']");
        const foodName = foodNameInput.value.trim();

        foodNameInput.setCustomValidity("");
        if (!foodName) {
            foodNameInput.setCustomValidity(translate("js.food_name_required"));
            return;
        }

        if (foodNames.has(foodName)) {
            foodNameInput.setCustomValidity(translate("js.duplicate_food_name"));
            return;
        }

        foodNames.add(foodName);
    });
}

function updateIntakeGramsValidity() {
    const foodInput = document.getElementById("food-inputs");
    const rows = foodInput.querySelectorAll("tr");

    rows.forEach((row) => {
        const minimumIntakeGramsInput = row.querySelector(
            "[name='food-minimum-intake-grams']",
        );
        const maximumIntakeGramsInput = row.querySelector(
            "[name='food-maximum-intake-grams']",
        );
        const minimumIntakeGrams = minimumIntakeGramsInput.valueAsNumber;
        const maximumIntakeGrams = maximumIntakeGramsInput.valueAsNumber;

        minimumIntakeGramsInput.setCustomValidity("");
        maximumIntakeGramsInput.setCustomValidity("");

        if (
            Number.isFinite(minimumIntakeGrams) &&
            !Number.isInteger(minimumIntakeGrams)
        ) {
            minimumIntakeGramsInput.setCustomValidity(
                translate("js.intake_grams_must_be_integer"),
            );
        }
        if (
            Number.isFinite(maximumIntakeGrams) &&
            !Number.isInteger(maximumIntakeGrams)
        ) {
            maximumIntakeGramsInput.setCustomValidity(
                translate("js.intake_grams_must_be_integer"),
            );
        }

        if (
            Number.isInteger(minimumIntakeGrams) &&
            Number.isInteger(maximumIntakeGrams) &&
            minimumIntakeGrams > maximumIntakeGrams
        ) {
            maximumIntakeGramsInput.setCustomValidity(
                translate("js.invalid_intake_grams_range"),
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
    updateFoodValidity();
    updateIntakeGramsValidity();

    const firstInvalidControl = getValidationControls().find(
        (control) => !control.checkValidity(),
    );

    if (firstInvalidControl) {
        firstInvalidControl.reportValidity();
        return false;
    }

    return true;
}
