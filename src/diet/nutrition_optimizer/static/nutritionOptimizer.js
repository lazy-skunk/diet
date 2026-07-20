import { translate } from "../../static/i18n.js";
import {
    buildOptimizePayload,
    validateOptimizeControls,
} from "./form.js";
import { handleOptimizationResult } from "./charts.js";

function getCsrfToken() {
    const csrfTokenMeta = document.querySelector("meta[name='csrf-token']");
    if (!(csrfTokenMeta instanceof HTMLMetaElement)) {
        throw new Error(translate("js.request_verification_failed"));
    }

    return csrfTokenMeta.content;
}

async function parseJsonResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        throw new Error(translate("js.unexpected_response"));
    }

    try {
        return await response.json();
    } catch {
        throw new Error(translate("js.unexpected_response"));
    }
}

export async function optimize() {
    const optimizeButton = document.getElementById("optimize");
    if (optimizeButton.disabled || !validateOptimizeControls()) {
        return;
    }

    optimizeButton.disabled = true;

    try {
        const payload = buildOptimizePayload();
        const csrfToken = getCsrfToken();
        let response;
        try {
            response = await fetch(optimizeButton.dataset.optimizeUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });
        } catch {
            throw new Error(translate("js.unexpected_response"));
        }

        const result = await parseJsonResponse(response);

        if (!response.ok) {
            const translationKey = result.errorCode
                ? `js.${result.errorCode}`
                : null;
            const translatedMessage = translationKey
                ? translate(translationKey)
                : null;
            const knownTranslatedMessage =
                translatedMessage !== translationKey
                    ? translatedMessage
                    : null;
            throw new Error(
                knownTranslatedMessage ||
                    translate("js.unexpected_response"),
            );
        }

        try {
            handleOptimizationResult(result);
        } catch {
            throw new Error(translate("js.unexpected_response"));
        }
    } catch (error) {
        if (error instanceof Error) {
            window.alert(error.message);
        }
    } finally {
        optimizeButton.disabled = false;
    }
}
