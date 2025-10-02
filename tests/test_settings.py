"""settings_test.py -- test the Settings Class
Tests the Settings Class by reading the imagenode.yaml file and parsing it
Tests that the Pydantic field validators are working correctly

To run this program, you must be in the project root directory
  that contains imagenode/ folder and tests/ folder
  and must have the appropriate virtualenv activated. Like this:

(py311cv4) jeffbass@jeff-mac-2022 ~/SDBdev2/imagenode $ pytest tests/test_settings.py

To have print() show even if tests pass, use the -s option

(py311cv4) jeffbass@jeff-mac-2022 ~/SDBdev2/imagenode $ pytest -s tests/test_settings.py

"""

import pytest
from pathlib import Path
from pydantic import ValidationError
from imagenode.tools.settings import Settings
from imagenode.tools.yaml_loader import load_yaml

CONFIGS_DIR = Path(__file__).parent / "test_yaml_files"
yaml_files = list(CONFIGS_DIR.glob("*.yaml"))

@pytest.mark.parametrize("yaml_file", yaml_files)
def test_settings_validation(yaml_file):
    raw_yaml = load_yaml(yaml_file)
    print("Yaml File: ", yaml_file)
    try:
        settings = Settings(**raw_yaml)
        settings.print_settings(raw_yaml=raw_yaml)
    except ValidationError as e:
        pytest.fail(f"Validation failed for {yaml_file.name}:\n{e}")
