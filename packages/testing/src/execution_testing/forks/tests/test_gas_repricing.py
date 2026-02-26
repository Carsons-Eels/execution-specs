"""Tests for gas repricing override mechanism."""

import json

import pytest

from ..forks.forks import Osaka, Prague
from ..forks.transition import PragueToOsakaAtTime15k
from ..gas_costs import GasCosts
from ..gas_repricing import _ENV_VAR, apply_repricing, load_repricing_config


@pytest.fixture(autouse=True)
def _clear_repricing_cache(monkeypatch):
    """Clear the lru_cache and env var before each test."""
    load_repricing_config.cache_clear()
    monkeypatch.delenv(_ENV_VAR, raising=False)


def _default_osaka_costs() -> GasCosts:
    return Osaka._base_gas_costs()


class TestLoadRepricingConfig:
    """Tests for load_repricing_config."""

    def test_no_env_var(self):
        """Test that the config is not loaded when the env var is unset."""
        config = load_repricing_config()
        assert config is None

    def test_empty_env_var(self, monkeypatch):
        """Test that the config is not loaded when the env var is null."""
        monkeypatch.setenv(_ENV_VAR, "")
        config = load_repricing_config()
        assert config is None

    def test_missing_file(self, monkeypatch):
        """Test that an error is raised when config is missing."""
        monkeypatch.setenv(_ENV_VAR, "/nonexistent/path.json")
        with pytest.raises(FileNotFoundError):
            load_repricing_config()

    def test_invalid_field_name(self, monkeypatch, tmp_path):
        """Test an invalid field name."""
        config_file = tmp_path / "bad.json"
        config_file.write_text(
            json.dumps({"Osaka": {"NOT_A_REAL_FIELD": 999}})
        )
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.raises(ValueError, match="NOT_A_REAL_FIELD"):
            load_repricing_config()

    def test_non_int_value_type(self, monkeypatch, tmp_path):
        """Test that a non-int value raises a type error."""
        config_file = tmp_path / "bad_type.json"
        config_file.write_text(
            json.dumps({"Osaka": {"GAS_TX_BASE": "not_a_number"}})
        )
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.raises(TypeError, match="must be of type int"):
            load_repricing_config()

    def test_valid_config(self, monkeypatch, tmp_path):
        """Test that a minimal valid config loads correctly."""
        config_file = tmp_path / "good.json"
        config_file.write_text(json.dumps({"Osaka": {"GAS_TX_BASE": 25000}}))
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        config = load_repricing_config()
        assert config == {"Osaka": {"GAS_TX_BASE": 25000}}

    def test_warning_emitted(self, monkeypatch, tmp_path):
        """Test that warnings are emitted when repricing has taken place."""
        config_file = tmp_path / "warn.json"
        config_file.write_text(json.dumps({"Osaka": {"GAS_TX_BASE": 1}}))
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.warns(UserWarning, match="Gas repricing config loaded"):
            load_repricing_config()


class TestApplyRepricing:
    """Tests for apply_repricing."""

    def test_no_config(self):
        """
        Test that costs are not altered when no repricing has taken place.
        """
        base = _default_osaka_costs()
        result = apply_repricing("Osaka", base)
        assert result is base

    def test_fork_not_in_config(self, monkeypatch, tmp_path):
        """
        Test that applying repricing for a different fork does not affect the
        values in Osaka.
        """
        config_file = tmp_path / "other.json"
        config_file.write_text(
            json.dumps({"Amsterdam": {"GAS_TX_BASE": 25000}})
        )
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        base = _default_osaka_costs()
        with pytest.warns(UserWarning):
            result = apply_repricing("Osaka", base)
        assert result is base

    def test_single_field_override(self, monkeypatch, tmp_path):
        """
        Test that repricing a single field does not affect the other fields.
        """
        config_file = tmp_path / "single.json"
        config_file.write_text(json.dumps({"Osaka": {"GAS_TX_BASE": 99999}}))
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        base = _default_osaka_costs()
        with pytest.warns(UserWarning):
            result = apply_repricing("Osaka", base)
        assert result.GAS_TX_BASE == 99999
        assert result.GAS_COLD_ACCOUNT_ACCESS == base.GAS_COLD_ACCOUNT_ACCESS


class TestIntegration:
    """Integration tests using the full gas_costs() path."""

    def test_osaka_gas_costs_with_override(self, monkeypatch, tmp_path):
        """Test that Osaka gas costs are properly overwritten by repricing."""
        config_file = tmp_path / "osaka.json"
        config_file.write_text(
            json.dumps({"Osaka": {"GAS_COLD_ACCOUNT_ACCESS": 2100}})
        )
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.warns(UserWarning):
            costs = Osaka.gas_costs()
        assert costs.GAS_COLD_ACCOUNT_ACCESS == 2100
        assert costs.GAS_TX_BASE == _default_osaka_costs().GAS_TX_BASE

    def test_osaka_gas_costs_without_override(self):
        """
        Test that default Osaka gas costs are not overwritten if gas costs
        are not repriced.
        """
        costs = Osaka.gas_costs()
        assert costs == _default_osaka_costs()

    def test_transition_fork_with_override(self, monkeypatch, tmp_path):
        """
        Test repricing during fork transition.
        """
        config_file = tmp_path / "transition.json"
        config_file.write_text(json.dumps({"Osaka": {"GAS_TX_BASE": 50000}}))
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.warns(UserWarning):
            costs = PragueToOsakaAtTime15k.gas_costs(timestamp=15000)
        assert costs.GAS_TX_BASE == 50000

    def test_transition_fork_pre_transition(self, monkeypatch, tmp_path):
        """
        Test that repricing a value in Osaka does not affect pre-transition
        prague cost.
        """
        config_file = tmp_path / "transition.json"
        config_file.write_text(json.dumps({"Osaka": {"GAS_TX_BASE": 50000}}))
        monkeypatch.setenv(_ENV_VAR, str(config_file))
        with pytest.warns(UserWarning):
            costs = PragueToOsakaAtTime15k.gas_costs(timestamp=0)
        assert costs.GAS_TX_BASE == Prague._base_gas_costs().GAS_TX_BASE
