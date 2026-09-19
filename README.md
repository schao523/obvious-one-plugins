# 明明可知 Obvious One

「明明可知 Obvious One」是可公開散布的 Codex 與 OpenClaw 技能插件 marketplace. The Obvious One marketplace publishes redistributable skill plugins with bilingual discovery metadata, deterministic artifacts, and auditable local runtimes.

## Vibe Coding Designer

`vibe-coding-designer` v1.0.0 guides product discovery and produces implementation-ready general-software specifications, data and workflow contracts, implementation prompts, traceable test plans, design reviews, and agent-neutral repository development packages. It supports GUI and non-GUI software and applies Web UI rules only when the product requires them.

Two deterministic editions are generated from the same verified source:

- `plugins/vibe-coding-designer` is the Codex artifact.
- `openclaw/vibe-coding-designer` is the lightweight OpenClaw artifact.

The plugin is skill-only: it bundles no private source documents, credentials, databases, vector indexes, models, or downloaded dependencies.

## 酷聖經教師 Cool Bible Tutor

`cool-bible-tutor` v2.4.6 是繁體中文歸納式聖經教師，涵蓋觀察、解釋、釋經處境、神學討論、原文／譯本比較與生活應用。The plugin provides the complete Bible Tutor v2.4 workflow; the church-ministry prompt-template module is intentionally excluded.

Two editions are generated from the same verified source:

- `plugins/cool-bible-tutor` is the fully bundled Codex artifact. It includes the public-domain PDFs, immutable 31,008-row verse database, compact semantic index, launcher, and pinned `rag_subsystem` wheel.
- `openclaw/cool-bible-tutor` is the lightweight OpenClaw artifact. Exact verse retrieval works immediately from its bundled database; explicit `setup-rag --accept-downloads` installs the shared runtime/model and downloads this plugin's independently owned index/PDF archives.

RAG only discovers candidate references. Exact quotations are always read again from the verified read-only verse database.

## Install in Codex

Clone this repository, register the checkout, and install a plugin:

```text
codex plugin marketplace add <absolute-path-to-this-checkout>
codex plugin add vibe-coding-designer@obvious-one
codex plugin add cool-bible-tutor@obvious-one
```

Start a new Codex task so the selected plugin's skills are loaded.

## Find and install in OpenClaw

Install directly from the Obvious One GitHub marketplace; this does not depend on ClawHub:

```text
openclaw plugins marketplace list schao523/obvious-one-plugins
openclaw plugins install vibe-coding-designer --marketplace schao523/obvious-one-plugins
openclaw plugins install cool-bible-tutor --marketplace schao523/obvious-one-plugins
```

After the Cool Bible Tutor ClawHub release is published, it also supports global search and a registry install:

```text
openclaw plugins search "酷聖經教師"
openclaw plugins search "Cool Bible Tutor"
openclaw plugins install clawhub:@obvious-one/cool-bible-tutor
```

Immediate Cool Bible Tutor exact lookup and optional semantic setup:

```text
python openclaw/cool-bible-tutor/scripts/cool_bible_tutor.py passage "約 3:16" --format json
python openclaw/cool-bible-tutor/scripts/cool_bible_tutor.py setup-rag --accept-downloads
```

See each artifact's `README.md`, `PRIVACY.md`, `SECURITY.md`, and `THIRD_PARTY_NOTICES.md` for setup, provenance, privacy, and dependency details.

Search terms: 明明可知, Obvious One, Vibe Coding Designer, software design, non-GUI software, 酷聖經教師, Cool Bible Tutor, 繁體中文查經, Traditional Chinese Bible study.
