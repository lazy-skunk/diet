import { currentLocale, translate } from "../../static/i18n.js";

const FOOD_PAGE_SIZE = 50;
const FOOD_SEARCH_DEBOUNCE_MS = 250;

let activeFoodRow = null;
let currentFoodPage = 1;
let foodPickerModal = null;
let foodCatalog = null;
let foodCatalogPromise = null;
let foodNutrientIndexes = new Map();
let foodSearchTimer = null;
let handleFoodSelected = null;
let nutrientDefinitions = [];

function translateWithValues(key, values) {
    return Object.entries(values).reduce(
        (message, [name, value]) =>
            message.replace(`{${name}}`, String(value)),
        translate(key),
    );
}

function parseNutrientNumericValue(value) {
    const normalizedValue = value.trim();
    if (["", "-", "*", "Tr"].includes(normalizedValue)) {
        return 0;
    }

    const valueWithoutParentheses = normalizedValue
        .replace(/^\(/, "")
        .replace(/\)$/, "");
    const numericValue = Number.parseFloat(valueWithoutParentheses);
    return Number.isFinite(numericValue) ? numericValue : 0;
}

async function fetchFoodCatalog() {
    const modalElement = document.getElementById("food-picker-modal");
    let response;
    try {
        response = await fetch(modalElement.dataset.foodCatalogUrl);
    } catch {
        throw new Error(translate("js.unexpected_response"));
    }
    if (!response.ok) {
        throw new Error(translate("js.unexpected_response"));
    }

    let catalogData;
    try {
        catalogData = await response.json();
    } catch {
        throw new Error(translate("js.unexpected_response"));
    }
    if (
        !Array.isArray(catalogData.nutrientIdentifiers) ||
        !Array.isArray(catalogData.foods)
    ) {
        throw new Error(translate("js.unexpected_response"));
    }

    foodNutrientIndexes = new Map(
        catalogData.nutrientIdentifiers.map((identifier, index) => [
            identifier,
            index,
        ]),
    );
    foodCatalog = catalogData.foods;
}

async function loadFoodCatalog() {
    if (foodCatalog !== null) {
        return;
    }

    if (foodCatalogPromise === null) {
        foodCatalogPromise = fetchFoodCatalog();
    }

    try {
        await foodCatalogPromise;
    } catch (error) {
        foodCatalogPromise = null;
        throw error;
    }
}

function formatNutrientLabel(definition) {
    if (!definition.displayUnit) {
        return definition.name;
    }

    return `${definition.name} (${definition.displayUnit})`;
}

function populateFoodSortOptions() {
    const sortBySelect = document.getElementById("food-sort-by");
    sortBySelect.querySelectorAll("[data-nutrient-sort-option]").forEach(
        (option) => option.remove(),
    );

    nutrientDefinitions.forEach((definition) => {
        const option = document.createElement("option");
        option.dataset.nutrientSortOption = "";
        option.value = definition.identifier;
        option.textContent = formatNutrientLabel(definition);
        option.title = definition.name;
        sortBySelect.appendChild(option);
    });
}

function getFoodNutrient(food, identifier) {
    const nutrientIndex = foodNutrientIndexes.get(identifier);
    if (nutrientIndex === undefined) {
        return null;
    }

    const value = food.values[nutrientIndex];
    if (!value) {
        return null;
    }

    return {
        value,
        numericValue: parseNutrientNumericValue(value),
    };
}

function createHeaderCell(definition) {
    const header = document.createElement("th");
    header.scope = "col";
    header.dataset.generatedPickerColumn = definition.identifier;
    header.textContent = formatNutrientLabel(definition);
    header.title = definition.name;
    return header;
}

function createPickerValueCell(food, definition) {
    const cell = document.createElement("td");
    const nutrient = getFoodNutrient(food, definition.identifier);
    cell.dataset.generatedPickerCell = definition.identifier;
    cell.textContent = nutrient?.value || "-";
    cell.title = definition.name;
    return cell;
}

function compareFoods(left, right, sortBy, sortOrder) {
    const direction = sortOrder === "asc" ? 1 : -1;

    if (sortBy === "name") {
        return left.name.localeCompare(right.name, currentLocale()) * direction;
    }

    const leftValue = getFoodNutrient(left, sortBy)?.numericValue || 0;
    const rightValue = getFoodNutrient(right, sortBy)?.numericValue || 0;
    if (leftValue === rightValue) {
        return left.name.localeCompare(right.name, currentLocale());
    }

    return (leftValue - rightValue) * direction;
}

function selectedFood(food) {
    return {
        name: food.name,
        nutrientValues: Object.fromEntries(
            nutrientDefinitions.map((definition) => [
                definition.identifier,
                getFoodNutrient(food, definition.identifier)?.numericValue ??
                    "",
            ]),
        ),
    };
}

function createPickerActionCell(food) {
    const cell = document.createElement("td");
    cell.dataset.staticPickerCell = "action";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn-sm btn-primary";
    button.textContent = "✓";
    button.title = translate("js.select");
    button.addEventListener("click", () => {
        if (!activeFoodRow) {
            return;
        }

        handleFoodSelected(activeFoodRow, selectedFood(food));
        foodPickerModal.hide();
    });

    cell.appendChild(button);
    return cell;
}

function updatePagination(resultCount, totalPages) {
    const resultCountElement = document.getElementById(
        "food-picker-result-count",
    );
    const pageNavigation = document.getElementById(
        "food-picker-page-navigation",
    );
    const pageStatus = document.getElementById("food-picker-page-status");
    const previousButton = document.getElementById("food-picker-previous");
    const nextButton = document.getElementById("food-picker-next");
    const emptyMessage = document.getElementById("food-picker-empty");

    resultCountElement.textContent = translateWithValues(
        "js.food_result_count",
        { count: resultCount },
    );
    emptyMessage.hidden = resultCount !== 0;
    pageNavigation.hidden = resultCount === 0;
    if (resultCount === 0) {
        return;
    }

    pageStatus.textContent = translateWithValues("js.food_page_status", {
        current: currentFoodPage,
        total: totalPages,
    });
    previousButton.disabled = currentFoodPage === 1;
    nextButton.disabled = currentFoodPage === totalPages;
}

function renderRows() {
    if (foodCatalog === null) {
        return;
    }

    const optionsBody = document.getElementById("food-picker-options");
    const headerRow = document.querySelector("#food-picker-table thead tr");
    const actionHeader = headerRow.querySelector(
        "[data-picker-static-column='action']",
    );
    const searchValue = document
        .getElementById("food-picker-search")
        .value.trim()
        .toLowerCase();
    const sortBy = document.getElementById("food-sort-by").value;
    const sortOrder = document.getElementById("food-sort-order").value;

    document
        .querySelectorAll("[data-generated-picker-column]")
        .forEach((element) => element.remove());
    nutrientDefinitions.forEach((definition) => {
        headerRow.insertBefore(createHeaderCell(definition), actionHeader);
    });

    const filteredFoods = foodCatalog
        .filter(
            (food) =>
                searchValue === "" ||
                food.name.toLowerCase().includes(searchValue),
        )
        .sort((left, right) => compareFoods(left, right, sortBy, sortOrder));

    const totalPages = Math.ceil(filteredFoods.length / FOOD_PAGE_SIZE);
    currentFoodPage = Math.min(currentFoodPage, Math.max(totalPages, 1));
    const pageStart = (currentFoodPage - 1) * FOOD_PAGE_SIZE;
    const displayedFoods = filteredFoods.slice(
        pageStart,
        pageStart + FOOD_PAGE_SIZE,
    );

    const fragment = document.createDocumentFragment();
    displayedFoods.forEach((food) => {
        const row = document.createElement("tr");
        const nameCell = document.createElement("td");
        nameCell.textContent = food.name;
        row.appendChild(nameCell);

        nutrientDefinitions.forEach((definition) => {
            row.appendChild(createPickerValueCell(food, definition));
        });
        row.appendChild(createPickerActionCell(food));
        fragment.appendChild(row);
    });

    optionsBody.replaceChildren(fragment);
    updatePagination(filteredFoods.length, totalPages);
}

async function openFoodPicker(triggerButton) {
    activeFoodRow = triggerButton.closest("tr");
    currentFoodPage = 1;
    window.clearTimeout(foodSearchTimer);
    foodSearchTimer = null;
    const searchInput = document.getElementById("food-picker-search");
    const loadingMessage = document.getElementById("food-picker-loading");
    const pickerTable = document.getElementById("food-picker-table");
    searchInput.value = "";

    foodPickerModal.show();
    if (foodCatalog === null) {
        loadingMessage.hidden = false;
        pickerTable.hidden = true;
        try {
            await loadFoodCatalog();
        } catch (error) {
            if (error instanceof Error) {
                window.alert(error.message);
            }
            foodPickerModal.hide();
            return;
        } finally {
            loadingMessage.hidden = true;
        }
        pickerTable.hidden = false;
    }

    renderRows();
}

export function addFoodPickerTrigger(root) {
    const triggerButton = root.querySelector("[data-food-picker-trigger]");
    if (triggerButton) {
        triggerButton.addEventListener("click", () =>
            openFoodPicker(triggerButton),
        );
    }
}

export function initializeFoodPicker(definitions, onFoodSelected) {
    nutrientDefinitions = definitions;
    handleFoodSelected = onFoodSelected;
    populateFoodSortOptions();

    const modalElement = document.getElementById("food-picker-modal");
    const searchInput = document.getElementById("food-picker-search");
    const sortBySelect = document.getElementById("food-sort-by");
    const sortOrderSelect = document.getElementById("food-sort-order");
    const previousButton = document.getElementById("food-picker-previous");
    const nextButton = document.getElementById("food-picker-next");

    foodPickerModal = new bootstrap.Modal(modalElement);
    const proteinDefinition = nutrientDefinitions.find(
        (definition) => definition.key === "protein",
    );
    if (proteinDefinition) {
        sortBySelect.value = proteinDefinition.identifier;
    }
    sortOrderSelect.value = "desc";

    searchInput.addEventListener("input", () => {
        window.clearTimeout(foodSearchTimer);
        foodSearchTimer = window.setTimeout(() => {
            foodSearchTimer = null;
            currentFoodPage = 1;
            renderRows();
        }, FOOD_SEARCH_DEBOUNCE_MS);
    });
    sortBySelect.addEventListener("change", () => {
        window.clearTimeout(foodSearchTimer);
        foodSearchTimer = null;
        currentFoodPage = 1;
        renderRows();
    });
    sortOrderSelect.addEventListener("change", () => {
        window.clearTimeout(foodSearchTimer);
        foodSearchTimer = null;
        currentFoodPage = 1;
        renderRows();
    });
    previousButton.addEventListener("click", () => {
        if (currentFoodPage > 1) {
            currentFoodPage -= 1;
            renderRows();
        }
    });
    nextButton.addEventListener("click", () => {
        currentFoodPage += 1;
        renderRows();
    });
}
