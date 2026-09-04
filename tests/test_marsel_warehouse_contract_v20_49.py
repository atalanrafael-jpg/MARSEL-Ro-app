from pathlib import Path
import importlib.util


SCRIPT = Path(__file__).parents[1] / "scripts" / "marsel_warehouse_contract_v20_48.py"
SPEC = importlib.util.spec_from_file_location("marsel_warehouse_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_warehouse_contract_uses_documented_root_endpoint():
    assert MODULE.API_ROOT == "https://api.roapp.io"
    assert MODULE.DOCUMENTED_PATH == "/warehouse/"
    assert f"{MODULE.API_ROOT}{MODULE.DOCUMENTED_PATH}" == "https://api.roapp.io/warehouse/"


def test_warehouse_contract_does_not_use_v2_namespace():
    endpoint = f"{MODULE.API_ROOT}{MODULE.DOCUMENTED_PATH}"
    assert "/v2/warehouse/" not in endpoint


def test_warehouse_diagnostic_is_read_only():
    assert MODULE.DOC.endswith("/reference/get-warehouses")
    assert "WRITE" not in MODULE.DOCUMENTED_PATH.upper()
