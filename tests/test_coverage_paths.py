"""Keep same-named modules distinct when coverage is consumed outside the checkout."""

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def test_coverage_xml_preserves_repository_relative_module_paths(tmp_path):
    for name in ("accounts", "attendance"):
        package = tmp_path / name
        package.mkdir()
        (package / "__init__.py").write_text("")
        (package / "models.py").write_text("value = 1\n")
    (tmp_path / "runner.py").write_text("import accounts.models\nimport attendance.models\n")
    config = Path(__file__).resolve().parents[1] / "pyproject.toml"
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("COV_CORE", "COVERAGE"))
    }
    env["COVERAGE_FILE"] = str(tmp_path / ".coverage")
    for args in (["run", "runner.py"], ["xml", "-o", "coverage.xml"]):
        result = subprocess.run(
            [sys.executable, "-m", "coverage", args[0], "--rcfile", str(config), *args[1:]],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    report = ET.parse(tmp_path / "coverage.xml")
    files = {node.attrib["filename"] for node in report.findall(".//class")}
    assert {"accounts/models.py", "attendance/models.py"} <= files
    assert {node.text for node in report.findall(".//source") if node.text} == {"."}
