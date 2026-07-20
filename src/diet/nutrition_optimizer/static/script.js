import {
    fillFoodRow,
    initializeConstraintRows,
    initializeFoodRows,
    initializeNutrientColumns,
} from "./form.js";
import { initializeFoodPicker } from "./foodCatalog.js";
import { optimize } from "./nutritionOptimizer.js";

document.addEventListener("DOMContentLoaded", () => {
    const nutrientDefinitions = initializeNutrientColumns();
    initializeFoodPicker(nutrientDefinitions, fillFoodRow);
    initializeFoodRows();
    initializeConstraintRows();
    document.getElementById("optimize").addEventListener("click", () => optimize());
});
