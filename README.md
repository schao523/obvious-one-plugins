# 明明可知 Obvious One

「明明可知 Obvious One」是可公開散布的 Codex 與 OpenClaw 技能插件 marketplace. The Obvious One marketplace publishes redistributable skill plugins with bilingual discovery metadata, deterministic artifacts, and auditable local runtimes.

## 酷聖經教師 Cool Bible Tutor

`cool-bible-tutor` v2.4.6 是繁體中文歸納式聖經教師，涵蓋觀察、解釋、釋經處境、神學討論、原文／譯本比較與生活應用。The plugin provides the complete Bible Tutor v2.4 workflow; the church-ministry prompt-template module is intentionally excluded.

Two editions are generated from the same verified source:

- `plugins/cool-bible-tutor` is the fully bundled Codex artifact. It includes the public-domain PDFs, immutable 31,008-row verse database, compact semantic index, launcher, and pinned `rag_subsystem` wheel.
- `openclaw/cool-bible-tutor` is the lightweight OpenClaw artifact. Exact verse retrieval works immediately from its bundled database; explicit `setup-rag --accept-downloads` installs the shared runtime/model and downloads this plugin's independently owned index/PDF archives.

RAG only discovers candidate references. Exact quotations are always read again from the verified read-only verse database.

## Install in Codex

Clone this repository, register the checkout, and install the plugin:

```text
codex plugin marketplace add <absolute-path-to-this-checkout>
codex plugin add cool-bible-tutor@obvious-one
```

Start a new Codex task so all eight skills are loaded.

## Find and install in OpenClaw

Install directly from the Obvious One GitHub marketplace; this does not depend on ClawHub:

```text
openclaw plugins marketplace list schao523/obvious-one-plugins
openclaw plugins install cool-bible-tutor --marketplace schao523/obvious-one-plugins
```

After the ClawHub release is published, it also supports global search and a registry install:

```text
openclaw plugins search "酷聖經教師"
openclaw plugins search "Cool Bible Tutor"
openclaw plugins install clawhub:@obvious-one/cool-bible-tutor
```

Immediate exact lookup and optional semantic setup:

```text
python openclaw/cool-bible-tutor/scripts/cool_bible_tutor.py passage "約 3:16" --format json
python openclaw/cool-bible-tutor/scripts/cool_bible_tutor.py setup-rag --accept-downloads
```

See each artifact's `README.md`, `PRIVACY.md`, `SECURITY.md`, and `THIRD_PARTY_NOTICES.md` for setup, provenance, privacy, and dependency details.

Search terms: 明明可知, Obvious One, 酷聖經教師, Cool Bible Tutor, 繁體中文查經, Traditional Chinese Bible study.
