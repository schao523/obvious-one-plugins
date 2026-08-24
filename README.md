# 明明可知 Obvious One

「明明可知 Obvious One」是可公開散布的 Codex 技能插件 marketplace。The Obvious One marketplace publishes redistributable Codex skill plugins with bilingual discovery metadata and auditable local runtimes.

## 酷聖經教師 Cool Bible Tutor

`cool-bible-tutor` v2.4.5 是繁體中文歸納式聖經教師，涵蓋觀察、解釋、釋經處境、神學討論、原文／譯本比較與生活應用。The plugin provides the complete Bible Tutor v2.4 teaching workflow; the church-ministry prompt-template module is intentionally excluded.

Marketplace 下載約 64 MiB，已包括兩份發布者聲明為公版的和合本 PDF、31,008 列唯讀經文資料庫、9,942 chunks 的精簡語意索引、啟動器，以及固定版本的 MIT `rag_subsystem` wheel。精確經文檢索離線立即可用：

```powershell
python plugins/cool-bible-tutor/scripts/cool_bible_tutor.py passage "約 3:16" --format json
```

主題式探索需要另行明確同意下載約 1.30 GB 的固定 embedding model，以及 hash-locked CPU runtime（安裝時預留約 6 GB）：

```powershell
python plugins/cool-bible-tutor/scripts/cool_bible_tutor.py setup-rag
```

RAG 只找候選引用；所有精確引文仍由內附唯讀資料庫重新讀取和驗證。

## Install locally

Clone this repository, then register its non-default marketplace and install the plugin:

```text
codex plugin marketplace add <absolute-path-to-this-checkout>
codex plugin add cool-bible-tutor@obvious-one
```

Start a new Codex task after installation so the eight skills are loaded. See the plugin's `README.md`, `PRIVACY.md`, `SECURITY.md`, and `THIRD_PARTY_NOTICES.md` for setup, privacy, provenance, and dependency details.

Search terms: 明明可知, Obvious One, 酷聖經教師, Cool Bible Tutor, 繁體中文查經, Traditional Chinese Bible study.
