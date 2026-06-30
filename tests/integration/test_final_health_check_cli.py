import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = "c:/Users/shs2rng/.conda/envs/trail_test/python.exe"


def run_cli(args):
    cmd = [PYTHON, "scripts/run_health_check.py", *args]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_run_pc_ports_only():
    data = run_cli(["--device", "pc_ports"])
    assert "pc_ports" in data


def test_run_vector_only():
    data = run_cli(["--device", "vector"])
    assert "vector" in data


def test_run_psu_only():
    data = run_cli(["--device", "psu"])
    assert "psu" in data
