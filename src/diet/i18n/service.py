from collections.abc import Mapping
from typing import Any

from flask import has_request_context, request, session, url_for

from diet.i18n.auth import AUTH_TRANSLATIONS
from diet.i18n.body_composition import BODY_COMPOSITION_TRANSLATIONS
from diet.i18n.common import COMMON_TRANSLATIONS
from diet.i18n.nutrition_optimizer import NUTRITION_OPTIMIZER_TRANSLATIONS

SUPPORTED_LANGUAGES = ("ja", "en")
DEFAULT_LANGUAGE = "ja"

TranslationCatalog = Mapping[str, Mapping[str, str]]


def _merge_translations(
    *catalogs: TranslationCatalog,
) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for catalog in catalogs:
        duplicate_keys = set(merged).intersection(catalog)
        if duplicate_keys:
            duplicates = ", ".join(sorted(duplicate_keys))
            raise ValueError(f"Duplicate translation keys: {duplicates}")
        merged.update(
            {key: dict(translations) for key, translations in catalog.items()}
        )
    return merged


TRANSLATIONS = _merge_translations(
    COMMON_TRANSLATIONS,
    AUTH_TRANSLATIONS,
    BODY_COMPOSITION_TRANSLATIONS,
    NUTRITION_OPTIMIZER_TRANSLATIONS,
)


def get_locale() -> str:
    if not has_request_context():
        return DEFAULT_LANGUAGE

    query_language = request.args.get("lang")
    if query_language in SUPPORTED_LANGUAGES:
        session["lang"] = query_language
        return query_language

    session_language = session.get("lang")
    if session_language in SUPPORTED_LANGUAGES:
        return session_language

    browser_language = request.accept_languages.best_match(SUPPORTED_LANGUAGES)
    return browser_language or DEFAULT_LANGUAGE


def translate(key: str) -> str:
    translations = TRANSLATIONS.get(key, {})
    return (
        translations.get(get_locale())
        or translations.get(DEFAULT_LANGUAGE)
        or key
    )


def localized_url(language: str) -> str:
    view_args: dict[str, Any] = (
        request.view_args.copy() if request.view_args else {}
    )
    query_args: dict[str, Any] = request.args.to_dict(flat=True)
    query_args["lang"] = language

    values = {**view_args, **query_args}

    return url_for(request.endpoint or "main.index", **values)


def javascript_translations() -> dict[str, str]:
    return {
        key: translate(key) for key in TRANSLATIONS if key.startswith("js.")
    }
