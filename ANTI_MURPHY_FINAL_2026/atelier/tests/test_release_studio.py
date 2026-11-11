"""Regressions supporting the updated visual investigation and structured route editor.
These validate real Python engine behavior, not mocked analytics.
"""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from atelier.service import Studio, StudioError


def test_structured_route_change_recalculates_and_persists():
    with TemporaryDirectory() as folder:
        studio = Studio(Path(folder))
        initial = studio.info()
        payload = {"stations": deepcopy(initial["stations"]), "orders": deepcopy(initial["orders"])}
        payload["orders"][0]["route"] = [
            ["CORTE", 6.0], ["CNC", 8.0], ["PINTURA", 5.0], ["MONTAGEM", 6.0]
        ]
        revised = studio.set_model(payload)
        assert revised["orders"][0]["route"] == payload["orders"][0]["route"]
        assert revised["run_id"] != initial["run_id"]
        assert Studio(Path(folder)).info()["orders"][0]["route"] == payload["orders"][0]["route"]


def test_invalid_route_does_not_replace_model():
    with TemporaryDirectory() as folder:
        studio = Studio(Path(folder))
        initial = studio.info()
        payload = {"stations": deepcopy(initial["stations"]), "orders": deepcopy(initial["orders"])}
        payload["orders"][0]["route"] = [["POSTO_INEXISTENTE", 3]]
        with pytest.raises((StudioError, ValueError)):
            studio.set_model(payload)
        assert studio.info()["orders"][0]["route"] == initial["orders"][0]["route"]


def test_dashboard_is_read_only_and_matches_motor_after_route_edit():
    with TemporaryDirectory() as folder:
        studio = Studio(Path(folder))
        initial = studio.info()
        payload = {"stations": deepcopy(initial["stations"]), "orders": deepcopy(initial["orders"])}
        payload["orders"][0]["route"][0][1] += 1
        updated = studio.set_model(payload)
        dashboard = studio.dashboards()
        assert dashboard["run_id"] == updated["run_id"]
        assert dashboard["scenarios"]["incident"]["metrics"]["total_cost"] == updated["metrics"]["incident"]["total_cost"]
        assert studio.info()["selected"] == updated["selected"]
