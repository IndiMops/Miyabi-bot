import logging
import logging.handlers
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import utils.logger  # noqa: F401  (configures the root logger handlers)
from utils import misc

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class GetVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        misc._git_revision.cache_clear()
        self.addCleanup(misc._git_revision.cache_clear)
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("BOT_VERSION", None)

    def test_build_version_wins_without_running_git(self) -> None:
        os.environ["BOT_VERSION"] = "0.2.0"
        with mock.patch.object(misc.subprocess, "check_output") as check_output:
            self.assertEqual(misc.get_version("0.0.1"), "0.2.0")
        check_output.assert_not_called()

    def test_blank_build_version_is_ignored(self) -> None:
        os.environ["BOT_VERSION"] = "   "
        with mock.patch.object(misc.subprocess, "check_output", return_value=b"abc1234\n"):
            self.assertEqual(misc.get_version("0.0.1"), "dev-abc1234")

    def test_git_revision_is_shown_for_local_checkout(self) -> None:
        with mock.patch.object(misc.subprocess, "check_output", return_value=b"abc1234\n"):
            self.assertEqual(misc.get_version("0.0.1"), "dev-abc1234")

    def test_missing_git_falls_back_and_is_queried_once(self) -> None:
        with mock.patch.object(
            misc.subprocess, "check_output", side_effect=FileNotFoundError("git")
        ) as check_output:
            for _ in range(3):
                self.assertEqual(misc.get_version("0.0.1"), "0.0.1")
        self.assertEqual(check_output.call_count, 1)

    def test_not_a_git_repository_falls_back(self) -> None:
        error = subprocess.CalledProcessError(128, ["git", "rev-parse"])
        with mock.patch.object(misc.subprocess, "check_output", side_effect=error):
            self.assertEqual(misc.get_version("0.0.1"), "0.0.1")

    def test_real_process_without_git_on_path(self) -> None:
        # Mirrors the Docker image: no git executable and no BOT_VERSION.
        env = {
            key: value
            for key, value in os.environ.items()
            if key.upper() in {"SYSTEMROOT", "TEMP", "TMP"}
        }
        env["PATH"] = str(Path(sys.executable).parent)
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        code = "from utils.misc import get_version; print('VERSION=' + get_version('9.9.9'))"
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=temp_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VERSION=9.9.9", result.stdout.splitlines())


class StandardLogRotationTests(unittest.TestCase):
    def test_standard_log_is_rotated(self) -> None:
        handlers = [
            handler
            for handler in logging.getLogger().handlers
            if isinstance(handler, logging.handlers.RotatingFileHandler)
            and Path(handler.baseFilename).name == "standard.log"
        ]
        self.assertEqual(len(handlers), 1)
        self.assertGreater(handlers[0].maxBytes, 0)
        self.assertGreater(handlers[0].backupCount, 0)
