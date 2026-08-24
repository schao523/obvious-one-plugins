"""Consent-gated private runtime setup for bundled semantic discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from typing import Literal


PLUGIN_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_LOCK_MANIFEST = PLUGIN_ROOT / "vendor" / "rag-runtime" / "runtime-lock.json"


class ConsentRequired(RuntimeError):
    pass


class UnsupportedRuntime(RuntimeError):
    pass


class IntegrityError(RuntimeError):
    pass


class RuntimeInstallError(RuntimeError):
    pass


CONFIG_KEYS = {
    "schema_version",
    "runtime_lock_id",
    "python_executable",
    "model_path",
    "model_revision",
    "model_digest",
    "completed_at",
}


@dataclass(frozen=True)
class RuntimePaths:
    root: Path
    config: Path
    venv: Path
    model_cache: Path
    staging: Path

    @classmethod
    def for_user(cls, app_data_override: Path | None = None) -> "RuntimePaths":
        if app_data_override is not None:
            base = Path(app_data_override).expanduser()
        elif sys.platform == "win32":
            base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
        root = (base / "ObviousOne" / "cool-bible-tutor").resolve()
        return cls(
            root=root,
            config=root / "config.json",
            venv=root / "rag-runtime",
            model_cache=root / "model-cache",
            staging=root / ".staging",
        )


@dataclass(frozen=True)
class RuntimeAssets:
    plugin_root: Path
    runtime_lock_id: str
    model_revision: str
    model_digest: str
    core_ready: bool


@dataclass(frozen=True)
class RuntimeLock:
    runtime_lock_id: str
    requirements: Path
    wheel: Path
    requirements_sha256: str
    wheel_sha256: str
    supported_platforms: tuple[str, ...]
    python_min: tuple[int, int]
    python_max: tuple[int, int]
    required_free_bytes: int
    index_urls: tuple[str, ...]
    model_download_manifest: Path
    model_download_manifest_sha256: str
    model_identity_digest: str


@dataclass(frozen=True)
class ModelFile:
    path: str
    url: str
    size: int
    sha256: str


@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    revision: str
    license: str
    identity_digest: str
    total_bytes: int
    files: tuple[ModelFile, ...]


@dataclass(frozen=True)
class RagSetupReport:
    status: Literal[
        "rag_setup_required", "rag_ready", "rag_incompatible", "rag_incomplete"
    ]
    core_ready: bool
    reasons: tuple[str, ...]
    python_executable: Path | None = None
    model_path: Path | None = None


def bundled_runtime_assets() -> RuntimeAssets:
    try:
        lock = json.loads(RUNTIME_LOCK_MANIFEST.read_text(encoding="utf-8"))
        model_path = PLUGIN_ROOT / str(lock["model_manifest"])
        model = json.loads(model_path.read_text(encoding="utf-8"))
        if _sha256_file(model_path) != str(lock["model_manifest_sha256"]):
            raise ValueError("model identity manifest digest mismatch")
        from rag_runtime import bundled_rag_index_status
        core_ready = bundled_rag_index_status()["status"] == "current"
        return RuntimeAssets(
            plugin_root=PLUGIN_ROOT,
            runtime_lock_id=str(lock["runtime_lock_id"]),
            model_revision=str(model["revision"]),
            model_digest=str(lock["model_manifest_sha256"]),
            core_ready=core_ready,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise IntegrityError("bundled runtime asset manifests are invalid") from error


def _inside(path: Path, parent: Path) -> bool:
    resolved = Path(path).resolve()
    root = Path(parent).resolve()
    return resolved == root or resolved.is_relative_to(root)


def inspect_rag_setup(paths: RuntimePaths, assets: RuntimeAssets) -> RagSetupReport:
    if not paths.config.is_file():
        if paths.staging.exists():
            return RagSetupReport(
                "rag_incomplete", assets.core_ready, ("staging exists without a valid config",)
            )
        return RagSetupReport(
            "rag_setup_required", assets.core_ready, ("private runtime config is missing",)
        )

    try:
        payload = json.loads(paths.config.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or set(payload) != CONFIG_KEYS:
            raise ValueError("private config keys do not match schema")
        if payload["schema_version"] != 1:
            raise ValueError("private config schema version is unsupported")
        python_executable = Path(str(payload["python_executable"])).expanduser().resolve()
        model_path = Path(str(payload["model_path"])).expanduser().resolve()
        if not python_executable.is_file() or not model_path.is_dir():
            raise ValueError("configured runtime path is missing")
        if _inside(python_executable, assets.plugin_root) or _inside(model_path, assets.plugin_root):
            raise ValueError("private runtime path points inside the installed plugin")
        if payload["runtime_lock_id"] != assets.runtime_lock_id:
            raise ValueError("runtime lock identity mismatch")
        if payload["model_revision"] != assets.model_revision:
            raise ValueError("model revision mismatch")
        if payload["model_digest"] != assets.model_digest:
            raise ValueError("model digest mismatch")
        if not str(payload["completed_at"]).strip():
            raise ValueError("runtime completion timestamp is missing")
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        return RagSetupReport("rag_incompatible", assets.core_ready, (str(error),))
    return RagSetupReport(
        "rag_ready",
        assets.core_ready,
        ("private runtime config matches bundled assets",),
        python_executable=python_executable,
        model_path=model_path,
    )


def select_runtime_lock(
    platform_tag: str,
    python_version: tuple[int, int],
    manifest_path: Path = RUNTIME_LOCK_MANIFEST,
) -> RuntimeLock:
    try:
        raw = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if raw.get("schema_version") != 1:
            raise ValueError("runtime lock schema is unsupported")
        root = Path(manifest_path).resolve().parents[2]
        lock = RuntimeLock(
            runtime_lock_id=str(raw["runtime_lock_id"]),
            requirements=root / str(raw["requirements"]),
            wheel=root / str(raw["wheel"]),
            requirements_sha256=str(raw["requirements_sha256"]),
            wheel_sha256=str(raw["wheel_sha256"]),
            supported_platforms=tuple(map(str, raw["supported_platforms"])),
            python_min=tuple(map(int, raw["python_min"])),
            python_max=tuple(map(int, raw["python_max"])),
            required_free_bytes=int(raw["required_free_bytes"]),
            index_urls=tuple(map(str, raw["index_urls"])),
            model_download_manifest=root / str(raw["model_download_manifest"]),
            model_download_manifest_sha256=str(raw["model_download_manifest_sha256"]),
            model_identity_digest=str(raw["model_manifest_sha256"]),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise UnsupportedRuntime("runtime lock manifest is invalid") from error
    if platform_tag not in lock.supported_platforms:
        raise UnsupportedRuntime(f"unsupported runtime platform: {platform_tag}")
    version = tuple(map(int, python_version))
    if not lock.python_min <= version <= lock.python_max:
        raise UnsupportedRuntime("RAG setup supports CPython 3.10 through 3.13")
    if not all(path.is_file() for path in (
        lock.requirements, lock.wheel, lock.model_download_manifest
    )):
        raise UnsupportedRuntime("runtime lock artifacts are incomplete")
    return lock


def load_model_manifest(lock: RuntimeLock) -> ModelManifest:
    if _sha256_file(lock.model_download_manifest) != lock.model_download_manifest_sha256:
        raise IntegrityError("model download manifest digest mismatch")
    try:
        raw = json.loads(lock.model_download_manifest.read_text(encoding="utf-8"))
        if raw.get("schema_version") != 1:
            raise ValueError("unsupported model manifest schema")
        manifest = ModelManifest(
            model_id=str(raw["model_id"]),
            revision=str(raw["revision"]),
            license=str(raw["license"]),
            identity_digest=str(raw["identity_manifest_sha256"]),
            total_bytes=int(raw["total_bytes"]),
            files=tuple(ModelFile(
                path=str(item["path"]),
                url=str(item["url"]),
                size=int(item["size"]),
                sha256=str(item["sha256"]),
            ) for item in raw["files"]),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise IntegrityError("model download manifest is invalid") from error
    if manifest.license != "MIT" or manifest.identity_digest != lock.model_identity_digest:
        raise IntegrityError("model identity or license binding mismatch")
    if len(manifest.revision) != 40 or not manifest.files:
        raise IntegrityError("model revision or file list is invalid")
    for item in manifest.files:
        _safe_relative_path(item.path)
        if not item.url.startswith("https://") or len(item.sha256) != 64 or item.size < 0:
            raise IntegrityError(f"invalid model file manifest entry: {item.path}")
    return manifest


def setup_rag(
    paths: RuntimePaths,
    assets: RuntimeAssets,
    *,
    consent: bool,
    runner,
    downloader,
    platform_tag: str,
    python_version: tuple[int, int],
    repair: bool = False,
):
    if not consent:
        raise ConsentRequired(
            "RAG setup requires consent before any dependency or model download"
        )
    lock = select_runtime_lock(platform_tag, python_version)
    manifest = load_model_manifest(lock)
    if (
        assets.runtime_lock_id != lock.runtime_lock_id
        or assets.model_revision != manifest.revision
        or assets.model_digest != manifest.identity_digest
    ):
        raise IntegrityError("bundled setup assets do not match the runtime lock")
    existing = inspect_rag_setup(paths, assets)
    if existing.status == "rag_ready" and not repair:
        return existing
    staged_venv = install_runtime(paths, lock, runner)
    staged_model = paths.staging / (
        f"model-{manifest.revision}-{manifest.identity_digest[:16]}"
    )
    try:
        download_model(manifest, staged_model, downloader)
        smoke_test_runtime(staged_venv, staged_model, assets, runner)
        activate_runtime(staged_venv, staged_model, paths, assets)
    except Exception:
        if staged_venv.exists() and _inside(staged_venv, paths.staging):
            shutil.rmtree(staged_venv)
        # Keep the private model staging directory so verified files and an
        # interrupted .partial transfer can be reused on the next consented run.
        raise
    return inspect_rag_setup(paths, assets)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _disk_anchor(path: Path) -> Path:
    candidate = Path(path).resolve()
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate


def _runtime_python(staged: Path) -> Path:
    return staged / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def _run_install_command(runner, command: list[str], label: str) -> None:
    try:
        completed = runner(command)
    except OSError as error:
        raise RuntimeInstallError(f"{label} could not be started") from error
    if int(getattr(completed, "returncode", 1)) != 0:
        raise RuntimeInstallError(f"{label} failed")


def install_runtime(
    paths: RuntimePaths,
    lock: RuntimeLock,
    runner,
    *,
    base_python: Path | None = None,
    disk_usage=shutil.disk_usage,
) -> Path:
    if _sha256_file(lock.requirements) != lock.requirements_sha256:
        raise IntegrityError("runtime requirements lock digest mismatch")
    if _sha256_file(lock.wheel) != lock.wheel_sha256:
        raise IntegrityError("rag_subsystem wheel digest mismatch")
    available = int(disk_usage(_disk_anchor(paths.root)).free)
    if available < lock.required_free_bytes:
        raise RuntimeInstallError(
            f"insufficient free space: required={lock.required_free_bytes} available={available}"
        )

    paths.staging.mkdir(parents=True, exist_ok=True)
    staged = paths.staging / f"runtime-{lock.runtime_lock_id[:16]}"
    if staged.exists():
        if not _inside(staged, paths.staging):
            raise RuntimeInstallError("staging path escaped the private runtime root")
        shutil.rmtree(staged)
    executable = Path(sys.executable if base_python is None else base_python).resolve()
    try:
        _run_install_command(
            runner, [str(executable), "-m", "venv", str(staged)], "venv creation"
        )
        staged_python = _runtime_python(staged)
        if not staged_python.is_file():
            raise RuntimeInstallError("venv creation did not produce a Python executable")
        _run_install_command(
            runner,
            [
                str(staged_python), "-m", "pip", "install",
                "--disable-pip-version-check", "--use-feature=truststore",
                "--require-hashes", "--no-input",
                "-r", str(lock.requirements),
            ],
            "hash-locked pip installation",
        )
        _run_install_command(
            runner,
            [
                str(staged_python), "-m", "pip", "install", "--no-deps",
                "--disable-pip-version-check", "--no-input", str(lock.wheel),
            ],
            "rag_subsystem wheel installation",
        )
    except Exception:
        if staged.exists() and _inside(staged, paths.staging):
            shutil.rmtree(staged)
        raise
    return staged


def _safe_relative_path(value: str) -> Path:
    relative = Path(value)
    if (
        not value
        or relative.is_absolute()
        or any(part in ("", ".", "..") for part in relative.parts)
    ):
        raise IntegrityError(f"unsafe model path: {value!r}")
    return relative


def download_model(
    manifest: ModelManifest,
    staging: Path,
    downloader,
) -> Path:
    if sum(item.size for item in manifest.files) != manifest.total_bytes:
        raise IntegrityError("model manifest total byte count mismatch")
    destination_root = Path(staging).resolve()
    destination_root.mkdir(parents=True, exist_ok=True)
    for item in manifest.files:
        relative = _safe_relative_path(item.path)
        destination = destination_root / relative
        if not _inside(destination, destination_root):
            raise IntegrityError(f"unsafe model path: {item.path!r}")
        if (
            destination.is_file()
            and destination.stat().st_size == item.size
            and _sha256_file(destination) == item.sha256
        ):
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        offset = partial.stat().st_size if partial.is_file() else 0
        if offset > item.size:
            partial.unlink()
            offset = 0
        try:
            completed = bool(downloader(item.url, partial, offset=offset))
            if not completed:
                partial.unlink(missing_ok=True)
                downloader(item.url, partial, offset=0)
        except OSError as error:
            raise RuntimeInstallError(f"model download failed: {item.path}") from error
        if (
            not partial.is_file()
            or partial.stat().st_size != item.size
            or _sha256_file(partial) != item.sha256
        ):
            partial.unlink(missing_ok=True)
            raise IntegrityError(f"model file digest mismatch: {item.path}")
        os.replace(partial, destination)
    return destination_root


def http_downloader(url: str, destination: Path, *, offset: int = 0) -> bool:
    headers = {"Accept-Encoding": "identity", "User-Agent": "cool-bible-tutor/2.4"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        status = int(getattr(response, "status", response.getcode()))
        content_range = str(response.headers.get("Content-Range", ""))
        resumed = bool(offset and status == 206 and content_range.startswith(f"bytes {offset}-"))
        mode = "ab" if resumed else "wb"
        with Path(destination).open(mode) as handle:
            shutil.copyfileobj(response, handle, length=1024 * 1024)
    return True


def smoke_test_runtime(
    staged_venv: Path,
    staged_model: Path,
    assets: RuntimeAssets,
    runner,
) -> None:
    python_executable = _runtime_python(Path(staged_venv))
    index = assets.plugin_root / "assets" / "rag" / "cuv-rag-index.sqlite3"
    if not python_executable.is_file() or not index.is_file():
        raise RuntimeInstallError("smoke-test assets are incomplete")
    script = (
        "import math,os;"
        "from sentence_transformers import SentenceTransformer;"
        "m=SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL_PATH'],device='cpu',local_files_only=True);"
        "v=m.encode(['神的愛與救恩'],normalize_embeddings=True,convert_to_numpy=True)[0].tolist();"
        "assert len(v)==1024 and all(math.isfinite(x) for x in v);"
        "from rag_subsystem import retrieve_data,DEFAULT_RETRIEVAL_CONFIG;"
        "r=retrieve_data('神的愛與救恩',top_k=3,filters={'app_id':'cool-bible-tutor'},"
        "config=DEFAULT_RETRIEVAL_CONFIG);"
        "assert r.results and any(x.chunk.metadata.get('canonical_reference') for x in r.results)"
    )
    environment = dict(os.environ)
    for key in tuple(environment):
        if key.startswith(("RAG_EMBEDDING_MODEL_PATH_", "RAG_EMBEDDING_MODEL_DIR_")):
            environment.pop(key, None)
    environment.update({
        "RAG_EMBEDDING_BACKEND": "local",
        "RAG_EMBEDDING_MODEL": "bge-large-zh",
        "RAG_EMBEDDING_MODEL_PATH": str(Path(staged_model).resolve()),
        "RAG_EMBEDDING_LOCAL_ONLY": "true",
        "RAG_VECTOR_STORE_BACKEND": "sqlite_readonly",
        "RAG_VECTOR_STORE_PATH": str(index.resolve()),
        "RAG_EMBEDDING_DIM": "1024",
    })
    try:
        completed = runner([str(python_executable), "-B", "-c", script], env=environment)
    except OSError as error:
        raise RuntimeInstallError("RAG smoke test could not be started") from error
    if int(getattr(completed, "returncode", 1)) != 0:
        raise RuntimeInstallError("RAG smoke test failed")


def _move_staged_directory(staged: Path, destination: Path) -> None:
    source = Path(staged).resolve()
    target = Path(destination).resolve()
    if not source.is_dir():
        raise RuntimeInstallError(f"staged directory is missing: {source.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if source != target:
            shutil.rmtree(source)
        return
    os.replace(source, target)


def activate_runtime(
    staged_venv: Path,
    staged_model: Path,
    paths: RuntimePaths,
    assets: RuntimeAssets,
) -> None:
    if not _inside(staged_venv, paths.staging) or not _inside(staged_model, paths.staging):
        raise RuntimeInstallError("activation source must be inside private staging")
    activation_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    runtime_destination = paths.venv / f"{assets.runtime_lock_id}-{activation_id}"
    model_destination = paths.model_cache / (
        f"{assets.model_revision}-{assets.model_digest[:16]}-{activation_id}"
    )
    _move_staged_directory(staged_venv, runtime_destination)
    _move_staged_directory(staged_model, model_destination)
    python_executable = _runtime_python(runtime_destination)
    if not python_executable.is_file() or not model_destination.is_dir():
        raise RuntimeInstallError("activated runtime is incomplete")

    payload = {
        "schema_version": 1,
        "runtime_lock_id": assets.runtime_lock_id,
        "python_executable": str(python_executable.resolve()),
        "model_path": str(model_destination.resolve()),
        "model_revision": assets.model_revision,
        "model_digest": assets.model_digest,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    paths.root.mkdir(parents=True, exist_ok=True)
    temporary = paths.root / "config.json.tmp"
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, paths.config)
