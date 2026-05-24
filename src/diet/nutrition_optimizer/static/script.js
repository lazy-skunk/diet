import {
    appendTemplateToTable,
    initializeNutrientSelectOnChange,
} from "./form.js";
import { optimize } from "./nutritionOptimizer.js";

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("add-food").addEventListener("click", () =>
        appendTemplateToTable("food-template", "food-inputs"),
    );
    initializeNutrientSelectOnChange();
    document.getElementById("add-constraint").addEventListener("click", () =>
        appendTemplateToTable("constraint-template", "constraint-inputs"),
    );
    document.getElementById("optimize").addEventListener("click", () => optimize());
});
