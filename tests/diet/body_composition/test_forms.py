from datetime import date

from flask import Flask
from pytest import MonkeyPatch

from diet.body_composition import forms as forms_module
from diet.body_composition.forms import RecordBodyCompositionForm


def test_record_body_composition_form_uses_current_date_per_instance(
    app: Flask, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(forms_module, "_today", lambda: date(2026, 5, 31))
    first_form = RecordBodyCompositionForm()

    monkeypatch.setattr(forms_module, "_today", lambda: date(2026, 6, 1))
    second_form = RecordBodyCompositionForm()

    assert first_form.date.data == date(2026, 5, 31)
    assert first_form.date.render_kw["max"] == "2026-05-31"
    assert second_form.date.data == date(2026, 6, 1)
    assert second_form.date.render_kw["max"] == "2026-06-01"
