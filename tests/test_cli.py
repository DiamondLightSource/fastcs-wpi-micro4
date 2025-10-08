import subprocess
import sys

from fastcs_wpi_micro4 import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "fastcs_wpi_micro4", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
