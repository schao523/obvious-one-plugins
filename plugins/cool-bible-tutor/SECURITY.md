# Security

Report security issues privately to the repository owner before public disclosure. Include the affected plugin version, platform, reproduction steps, and relevant non-sensitive logs.

The release security boundary is enforced by `scripts/distribution_audit.py` and `scripts/build_marketplace_release.py`. Bundled databases, PDFs, the compact index, dependency lock, subsystem wheel, and model manifest are digest-bound. `setup-rag` uses argument-array subprocess execution, hash-locked Python packages, immutable model URLs, safe relative paths, private staging, offline smoke verification, and config-last atomic activation.

Never add credentials, private review data, authoring databases, unapproved PDFs, model weights, caches, or machine-specific paths to the plugin tree. Do not disable TLS or digest verification to work around a setup failure.

Supported releases receive fixes on the latest tagged `cool-bible-tutor-v2.4.x` line. Users should verify release tags and rerun `python scripts/cool_bible_tutor.py status --json` after an upgrade.
