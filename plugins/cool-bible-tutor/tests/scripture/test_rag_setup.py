import json
from dataclasses import replace
from pathlib import Path
import shutil
import sys
import unittest


SCRIPTS = (
    Path(__file__).parents[2]
    / "skills"
    / "retrieving-chinese-union-version-scripture"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))
RUNTIME = Path(__file__).parents[1] / "_runtime_fixture" / "rag-setup"

from rag_setup import (  # noqa: E402
    ConsentRequired,
    ModelFile,
    ModelManifest,
    RuntimeAssets,
    RuntimePaths,
    IntegrityError,
    RuntimeInstallError,
    UnsupportedRuntime,
    activate_runtime,
    download_model,
    inspect_rag_setup,
    install_runtime,
    select_runtime_lock,
    setup_rag,
    smoke_test_runtime,
)


class RecordingRunner:
    def __init__(self, fail_at=None):
        self.commands = []
        self.fail_at = fail_at

    def __call__(self, command, **kwargs):
        self.commands.append((list(command), kwargs))
        if len(command) >= 4 and command[1:3] == ["-m", "venv"]:
            staged = Path(command[3])
            python = staged / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            python.parent.mkdir(parents=True, exist_ok=True)
            python.touch()
        return type(
            "Completed", (), {"returncode": 1 if self.fail_at == len(self.commands) else 0}
        )()


class RecordingDownloader:
    def __init__(self, payloads=None, corrupt=()):
        self.requests = []
        self.payloads = payloads or {}
        self.corrupt_paths = set(corrupt)

    def __call__(self, url, destination, *, offset=0):
        self.requests.append((url, Path(destination), offset))
        relative = url.rsplit("/", 1)[-1]
        payload = self.payloads[relative]
        if relative in self.corrupt_paths:
            payload += b"corrupt"
        mode = "ab" if offset else "wb"
        with Path(destination).open(mode) as handle:
            handle.write(payload[offset:])
        return True


class RagSetupStateTests(unittest.TestCase):
    def setUp(self):
        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)
        RUNTIME.mkdir(parents=True)
        self.plugin_root = RUNTIME / "installed-plugin"
        self.plugin_root.mkdir()
        self.paths = RuntimePaths.for_user(RUNTIME / "app-data")
        self.assets = RuntimeAssets(
            plugin_root=self.plugin_root,
            runtime_lock_id="lock-sha256",
            model_revision="a" * 40,
            model_digest="b" * 64,
            core_ready=True,
        )

    def tearDown(self):
        if RUNTIME.exists():
            shutil.rmtree(RUNTIME)

    def test_runtime_paths_are_outside_plugin_and_stable(self):
        self.assertEqual(
            self.paths.root,
            (RUNTIME / "app-data" / "ObviousOne" / "cool-bible-tutor").resolve(),
        )
        self.assertEqual(self.paths.config, self.paths.root / "config.json")
        self.assertEqual(self.paths.venv, self.paths.root / "rag-runtime")
        self.assertEqual(self.paths.model_cache, self.paths.root / "model-cache")
        self.assertEqual(self.paths.staging, self.paths.root / ".staging")

    def test_missing_runtime_requires_setup_but_core_remains_ready(self):
        report = inspect_rag_setup(self.paths, self.assets)
        self.assertEqual(report.status, "rag_setup_required")
        self.assertTrue(report.core_ready)
        self.assertIn("config", " ".join(report.reasons))

    def test_staging_without_valid_config_is_incomplete(self):
        self.paths.staging.mkdir(parents=True)
        report = inspect_rag_setup(self.paths, self.assets)
        self.assertEqual(report.status, "rag_incomplete")
        self.assertTrue(report.core_ready)

    def write_ready_config(self):
        python = self.paths.venv / "v1" / ("python.exe" if sys.platform == "win32" else "bin/python")
        model = self.paths.model_cache / "model-v1"
        python.parent.mkdir(parents=True)
        python.touch()
        model.mkdir(parents=True)
        self.paths.root.mkdir(parents=True, exist_ok=True)
        self.paths.config.write_text(json.dumps({
            "schema_version": 1,
            "runtime_lock_id": self.assets.runtime_lock_id,
            "python_executable": str(python),
            "model_path": str(model),
            "model_revision": self.assets.model_revision,
            "model_digest": self.assets.model_digest,
            "completed_at": "2026-08-24T00:00:00Z",
        }), encoding="utf-8")
        return python, model

    def test_matching_private_config_is_ready(self):
        python, model = self.write_ready_config()
        report = inspect_rag_setup(self.paths, self.assets)
        self.assertEqual(report.status, "rag_ready")
        self.assertEqual(report.python_executable, python.resolve())
        self.assertEqual(report.model_path, model.resolve())

    def test_identity_path_and_schema_mismatches_are_incompatible(self):
        python, _model = self.write_ready_config()
        payload = json.loads(self.paths.config.read_text(encoding="utf-8"))
        payload["runtime_lock_id"] = "wrong"
        self.paths.config.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(inspect_rag_setup(self.paths, self.assets).status, "rag_incompatible")

        payload["runtime_lock_id"] = self.assets.runtime_lock_id
        payload["unknown"] = True
        self.paths.config.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(inspect_rag_setup(self.paths, self.assets).status, "rag_incompatible")

        payload.pop("unknown")
        payload["python_executable"] = str(self.plugin_root / "private-python.exe")
        Path(payload["python_executable"]).touch()
        self.paths.config.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(inspect_rag_setup(self.paths, self.assets).status, "rag_incompatible")
        self.assertTrue(python.is_file())

    def test_selects_exact_platform_lock(self):
        lock = select_runtime_lock("windows-x86_64", (3, 11))
        self.assertEqual(lock.requirements.name, "requirements-rag.lock")
        self.assertIn("windows-x86_64", lock.supported_platforms)
        self.assertEqual(lock.python_min, (3, 10))
        self.assertEqual(lock.python_max, (3, 13))

    def test_rejects_python_outside_supported_range(self):
        with self.assertRaisesRegex(UnsupportedRuntime, "3.10 through 3.13"):
            select_runtime_lock("windows-x86_64", (3, 14))
        with self.assertRaisesRegex(UnsupportedRuntime, "platform"):
            select_runtime_lock("linux-arm64", (3, 11))

    def test_setup_without_consent_executes_nothing(self):
        runner = RecordingRunner()
        downloader = RecordingDownloader()
        with self.assertRaisesRegex(ConsentRequired, "download"):
            setup_rag(
                self.paths,
                self.assets,
                consent=False,
                runner=runner,
                downloader=downloader,
                platform_tag="windows-x86_64",
                python_version=(3, 11),
            )
        self.assertEqual(runner.commands, [])
        self.assertEqual(downloader.requests, [])
        self.assertFalse(self.paths.root.exists())

    def synthetic_lock(self):
        requirements = RUNTIME / "requirements.lock"
        wheel = RUNTIME / "rag_subsystem.whl"
        requirements.write_text("fixture==1.0 --hash=sha256:" + "0" * 64, encoding="utf-8")
        wheel.write_bytes(b"synthetic wheel")
        selected = select_runtime_lock("windows-x86_64", (3, 11))
        import hashlib
        return replace(
            selected,
            requirements=requirements,
            wheel=wheel,
            requirements_sha256=hashlib.sha256(requirements.read_bytes()).hexdigest(),
            wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
            required_free_bytes=1,
        )

    def synthetic_model_manifest(self):
        import hashlib
        payloads = {"config.json": b"configuration", "model.bin": b"model-weights"}
        files = tuple(
            ModelFile(
                path=name,
                url=f"https://models.example.invalid/{name}",
                size=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
            for name, payload in payloads.items()
        )
        return ModelManifest(
            model_id="fixture/model",
            revision=self.assets.model_revision,
            license="MIT",
            identity_digest=self.assets.model_digest,
            total_bytes=sum(map(len, payloads.values())),
            files=files,
        ), payloads

    def test_model_download_reuses_verified_files_and_resumes_partial(self):
        manifest, payloads = self.synthetic_model_manifest()
        staged = self.paths.staging / "model"
        staged.mkdir(parents=True)
        (staged / "config.json").write_bytes(payloads["config.json"])
        (staged / "model.bin.partial").write_bytes(payloads["model.bin"][:5])
        downloader = RecordingDownloader(payloads)

        result = download_model(manifest, staged, downloader)

        self.assertEqual(result, staged)
        self.assertEqual([item[0] for item in downloader.requests], [
            "https://models.example.invalid/model.bin"
        ])
        self.assertEqual(downloader.requests[0][2], 5)
        self.assertEqual((staged / "model.bin").read_bytes(), payloads["model.bin"])
        self.assertFalse((staged / "model.bin.partial").exists())

    def test_model_download_rejects_unsafe_paths_and_bad_digest(self):
        manifest, payloads = self.synthetic_model_manifest()
        unsafe = replace(
            manifest,
            files=(replace(manifest.files[0], path="../escape"),),
            total_bytes=manifest.files[0].size,
        )
        with self.assertRaisesRegex(IntegrityError, "unsafe"):
            download_model(unsafe, self.paths.staging / "unsafe", RecordingDownloader(payloads))

        downloader = RecordingDownloader(payloads, corrupt={"model.bin"})
        with self.assertRaisesRegex(IntegrityError, "model.bin"):
            download_model(manifest, self.paths.staging / "corrupt", downloader)

    def test_atomic_activation_writes_config_last_and_preserves_previous_versions(self):
        staged_venv = self.paths.staging / "runtime-new"
        staged_python = staged_venv / (
            "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
        )
        staged_python.parent.mkdir(parents=True)
        staged_python.touch()
        staged_model = self.paths.staging / "model-new"
        staged_model.mkdir(parents=True)
        (staged_model / "config.json").write_text("{}", encoding="utf-8")
        old_runtime = self.paths.venv / "old"
        old_model = self.paths.model_cache / "old"
        old_runtime.mkdir(parents=True)
        old_model.mkdir(parents=True)

        activate_runtime(staged_venv, staged_model, self.paths, self.assets)

        payload = json.loads(self.paths.config.read_text(encoding="utf-8"))
        self.assertEqual(payload["runtime_lock_id"], self.assets.runtime_lock_id)
        self.assertEqual(payload["model_revision"], self.assets.model_revision)
        self.assertTrue(Path(payload["python_executable"]).is_file())
        self.assertTrue(Path(payload["model_path"]).is_dir())
        self.assertTrue(old_runtime.is_dir())
        self.assertTrue(old_model.is_dir())
        self.assertFalse((self.paths.root / "config.json.tmp").exists())

    def test_smoke_test_ignores_legacy_model_specific_override(self):
        staged_venv = self.paths.staging / "runtime-smoke"
        python = staged_venv / (
            "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
        )
        python.parent.mkdir(parents=True)
        python.touch()
        staged_model = self.paths.staging / "model-smoke"
        staged_model.mkdir(parents=True)
        index = self.plugin_root / "assets" / "rag" / "cuv-rag-index.sqlite3"
        index.parent.mkdir(parents=True)
        index.touch()
        runner = RecordingRunner()
        from unittest.mock import patch
        with patch.dict(
            "os.environ",
            {"RAG_EMBEDDING_MODEL_PATH_BGE_LARGE_ZH": "D:/legacy/model"},
            clear=True,
        ):
            smoke_test_runtime(staged_venv, staged_model, self.assets, runner)
        environment = runner.commands[-1][1]["env"]
        self.assertNotIn("RAG_EMBEDDING_MODEL_PATH_BGE_LARGE_ZH", environment)
        self.assertEqual(
            environment["RAG_EMBEDDING_MODEL_PATH"], str(staged_model.resolve())
        )

    def test_install_runtime_uses_hash_locked_argument_arrays(self):
        runner = RecordingRunner()
        lock = self.synthetic_lock()
        staged = install_runtime(
            self.paths,
            lock,
            runner,
            base_python=Path(sys.executable),
            disk_usage=lambda _path: type("Usage", (), {"free": 10})(),
        )

        staged_python = staged / (
            "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
        )
        self.assertEqual(runner.commands[0][0], [sys.executable, "-m", "venv", str(staged)])
        self.assertEqual(
            runner.commands[1][0],
            [
                str(staged_python), "-m", "pip", "install",
                "--disable-pip-version-check", "--use-feature=truststore",
                "--require-hashes", "--no-input",
                "-r", str(lock.requirements),
            ],
        )
        self.assertEqual(
            runner.commands[2][0],
            [
                str(staged_python), "-m", "pip", "install", "--no-deps",
                "--disable-pip-version-check", "--no-input", str(lock.wheel),
            ],
        )

    def test_integrity_or_install_failure_preserves_existing_config(self):
        self.paths.root.mkdir(parents=True)
        self.paths.config.write_text("previous config", encoding="utf-8")
        lock = self.synthetic_lock()
        bad_lock = replace(lock, wheel_sha256="f" * 64)
        runner = RecordingRunner()
        with self.assertRaisesRegex(IntegrityError, "wheel"):
            install_runtime(
                self.paths,
                bad_lock,
                runner,
                disk_usage=lambda _path: type("Usage", (), {"free": 10})(),
            )
        self.assertEqual(runner.commands, [])
        self.assertEqual(self.paths.config.read_text(encoding="utf-8"), "previous config")

        failing = RecordingRunner(fail_at=2)
        with self.assertRaisesRegex(RuntimeInstallError, "pip"):
            install_runtime(
                self.paths,
                lock,
                failing,
                disk_usage=lambda _path: type("Usage", (), {"free": 10})(),
            )
        self.assertEqual(self.paths.config.read_text(encoding="utf-8"), "previous config")

    def test_generated_lock_is_exact_hashed_and_cpu_only(self):
        lock = select_runtime_lock("windows-x86_64", (3, 11))
        content = lock.requirements.read_text(encoding="utf-8")
        logical_lines = []
        current = ""
        for raw in content.splitlines():
            stripped = raw.strip()
            if (
                not stripped
                or stripped.startswith("#")
                or (stripped.startswith("--") and not stripped.startswith("--hash="))
            ):
                continue
            if stripped.startswith("--hash="):
                current += " " + stripped
            else:
                if current:
                    logical_lines.append(current)
                current = stripped
            if not stripped.endswith("\\") and current:
                logical_lines.append(current)
                current = ""
        if current:
            logical_lines.append(current)
        for requirement in logical_lines:
            self.assertIn("==", requirement)
            self.assertIn("--hash=sha256:", requirement)
        self.assertIn("torch==2.13.0+cpu", content)
        self.assertNotIn("cuda-toolkit", content)
        self.assertNotIn("triton==", content)


if __name__ == "__main__":
    unittest.main()
    activate_runtime,
    download_model,
