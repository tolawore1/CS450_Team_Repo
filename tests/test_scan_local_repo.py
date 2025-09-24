from pathlib import Path
from ai_model_catalog.cli import _scan_local_repo


def test_scan_local_repo(tmp_path: Path):
    (tmp_path / "README.md").write_text("# demo\n")
    (tmp_path / "LICENSE").write_text("MIT\n")
    (tmp_path / "script.py").write_text("print('ok')\n")
    tdir = tmp_path / "tests"
    tdir.mkdir()
    (tdir / "test_x.py").write_text("def test_ok(): pass\n")

    data = _scan_local_repo(tmp_path)
    assert data["source"] == "local"
    assert data["has_readme"] is True
    assert data["license_file"] != ""
    assert data["py_files"] >= 2  # script.py + test_x.py
    assert data["test_files"] >= 1
    assert data["file_count"] >= 3
