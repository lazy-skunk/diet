import pytest

from diet.i18n.service import (
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    _merge_translations,
)


def test_all_translations_support_every_language() -> None:
    expected_languages = set(SUPPORTED_LANGUAGES)

    for translations in TRANSLATIONS.values():
        assert set(translations) == expected_languages


def test_translation_catalog_merge_rejects_duplicate_keys() -> None:
    with pytest.raises(ValueError, match="Duplicate translation keys: shared"):
        _merge_translations(
            {"shared": {"ja": "共有", "en": "Shared"}},
            {"shared": {"ja": "重複", "en": "Duplicate"}},
        )
