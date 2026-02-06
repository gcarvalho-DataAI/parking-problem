from __future__ import annotations

import os
import sys
from pathlib import Path
from _pytest.terminal import TerminalWriter


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def pytest_configure(config):
    _load_dotenv()
    log_only = os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true"
    if os.getenv("DEBUG", "").lower() == "true" and not log_only:
        config.option.capture = "no"
    if log_only:
        # Silence pytest terminal output
        config.option.capture = "fd"
        config.option.verbose = 0
        config.option.reportchars = ""
        config.option.showcapture = "no"
        reporter = config.pluginmanager.getplugin("terminalreporter")
        if reporter is not None:
            reporter._tw = TerminalWriter(file=open(os.devnull, "w"))

    if getattr(config, "getoption", None):
        if config.getoption("--plot"):
            os.environ["PLOT_CONVERGENCE"] = "true"


_LOG_FILE = None
_ORIG_STDOUT = None
_ORIG_STDERR = None
_DEVNULL = None


def pytest_load_initial_conftests(early_config, parser, args):
    _load_dotenv()
    if os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true":
        global _DEVNULL, _ORIG_STDOUT, _ORIG_STDERR
        _DEVNULL = open(os.devnull, "w")
        _ORIG_STDOUT = sys.stdout
        _ORIG_STDERR = sys.stderr
        sys.stdout = _DEVNULL
        sys.stderr = _DEVNULL


def pytest_addoption(parser):
    parser.addoption(
        "--plot",
        action="store_true",
        default=False,
        help="Generate convergence plots for each run",
    )


class _Tee:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self._streams:
            s.flush()


def pytest_sessionstart(session):
    _load_dotenv()
    log_path = os.getenv("TEST_LOG_FILE", "tests/output.log")
    log_only = os.getenv("LOG_TO_FILE_ONLY", "").lower() == "true"
    per_run = os.getenv("PER_RUN_LOG", "").lower() == "true"
    global _DEVNULL
    if log_only:
        _DEVNULL = open(os.devnull, "w")
        sys.stdout = _DEVNULL
        sys.stderr = _DEVNULL
    if per_run:
        return
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    global _LOG_FILE, _ORIG_STDOUT, _ORIG_STDERR
    _LOG_FILE = log_file.open("w", encoding="utf-8")
    _ORIG_STDOUT = sys.stdout
    _ORIG_STDERR = sys.stderr
    if log_only:
        sys.stdout = _LOG_FILE
        sys.stderr = _LOG_FILE
    else:
        sys.stdout = _Tee(sys.stdout, _LOG_FILE)
        sys.stderr = _Tee(sys.stderr, _LOG_FILE)


def pytest_sessionfinish(session, exitstatus):
    global _LOG_FILE, _ORIG_STDOUT, _ORIG_STDERR, _DEVNULL
    if _LOG_FILE is None:
        if _DEVNULL is not None:
            sys.stdout = _ORIG_STDOUT or sys.__stdout__
            sys.stderr = _ORIG_STDERR or sys.__stderr__
            _DEVNULL.close()
        return
    if _ORIG_STDOUT is not None:
        sys.stdout = _ORIG_STDOUT
    if _ORIG_STDERR is not None:
        sys.stderr = _ORIG_STDERR
    if _LOG_FILE is not None:
        _LOG_FILE.close()
    if _DEVNULL is not None:
        _DEVNULL.close()
    _LOG_FILE = None
    _ORIG_STDOUT = None
    _ORIG_STDERR = None
    _DEVNULL = None
