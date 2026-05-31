import {
    buildOptimizePayload,
    validateOptimizeControls,
} from "./form.js";
import { handleOptimizationResult } from "./charts.js";

function getCsrfToken() {
    const csrfTokenMeta = document.querySelector("meta[name='csrf-token']");
    if (!(csrfTokenMeta instanceof HTMLMetaElement)) {
        throw new Error("CSRF token is missing");
    }

    return csrfTokenMeta.content;
}

export async function optimize() {
    try {
        const optimizeButton = document.getElementById("optimize");
        if (!validateOptimizeControls()) {
            return;
        }

        const payload = buildOptimizePayload();
        const response = await fetch(optimizeButton.dataset.optimizeUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.message || `Response status: ${response.status}`,
            );
        }

        handleOptimizationResult(result);
    } catch (error) {
        if (error instanceof Error) {
            window.alert(error.message);
        }
    }
}
