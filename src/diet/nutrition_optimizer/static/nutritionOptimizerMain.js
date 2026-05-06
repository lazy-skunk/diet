import { addEventListenerToActionButton } from "./nutritionOptimizerDomUtilities.js";
import {
    appendTemplateToTable,
    initializeNutrientSelectOnChange,
    optimize,
} from "./nutritionOptimizer.js";

document.addEventListener("DOMContentLoaded", () => {
    addEventListenerToActionButton("add-food", () =>
        appendTemplateToTable("food-template", "food-inputs"),
    );
    initializeNutrientSelectOnChange();
    addEventListenerToActionButton("add-constraint", () =>
        appendTemplateToTable("constraint-template", "constraint-inputs"),
    );
    addEventListenerToActionButton("optimize", () => optimize());
});
