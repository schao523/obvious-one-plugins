# 設定和合本檢索資料

插件內附兩份經擁有者聲明為公版、並以 SHA-256 鎖定的和合本 PDF；建置、驗證與人工核對預設使用這一組來源。插件**不會自動下載**聖經、OCR 模型或第三方語料。請自行準備 Poppler（`pdfinfo`、`pdftotext`、`pdftoppm`）、Tesseract 及 `chi_tra` 語言資料。建置器優先使用可解析的嵌入 PDF 文字；沒有可用文字的頁面才退回影像 OCR。

## 建議入口

從插件根目錄使用頂層啟動器；它統一解析外部資料目錄並委派下列底層工具：

```text
python scripts/cool_bible_tutor.py doctor
python scripts/cool_bible_tutor.py init --data-dir <私有資料目錄>
python scripts/cool_bible_tutor.py status --data-dir <私有資料目錄> --json
python scripts/cool_bible_tutor.py verify --data-dir <私有資料目錄> --json
python scripts/cool_bible_tutor.py review --data-dir <私有資料目錄>
python scripts/cool_bible_tutor.py passage "約 3:16" --data-dir <私有資料目錄> --format json
```

啟動器不下載或安裝依賴、不自動核實 OCR，也拒絕把生成資料寫進插件。以下直接腳本介面保留給進階來源覆寫與除錯。

## 建立索引

從本技能目錄執行；不提供來源參數時，程式會核對並使用插件內附的兩份 PDF：

```text
python scripts/build_cuv_index.py --data-dir <私有資料目錄>
```

若要使用經授權的外部版本，必須同時提供 `--old-testament <舊約.pdf>` 與 `--new-testament <新約.pdf>`；只提供其中一份會被拒絕。

若 `chi_tra.traineddata` 不在 Tesseract 的預設目錄，可另加 `--tessdata-dir <語言資料目錄>`。這對含非 ASCII 字元的工作區尤其可靠，因為 Tesseract 會直接收到明確目錄，而不依賴全域環境變數。

若 Windows Tesseract 無法開啟含非 ASCII 字元的暫存影像路徑，可加 `--scratch-dir <純 ASCII 暫存目錄>`。資料庫與建置狀態仍留在 `--data-dir`；暫存目錄只存當頁影像，無論成功或失敗都會逐頁刪除。

資料目錄必須可寫且不得位於要分享的插件目錄。建置可在中斷後依 `build-state.json` 恢復；只有完整成功才會原子替換 `cuv.sqlite3`。

## 驗證索引

```text
python scripts/verify_cuv_index.py <私有資料目錄>/cuv.sqlite3 --json
```

驗證器預設核對內附 PDF；外部版本可重複使用 `--source-pdf <PDF>` 覆寫。只有報告 `production_ready: true` 且檢索退出碼為 0 的範圍，才能當作已核實精確引文。

## 以瀏覽器逐頁人工核對

核對工具只在本機 `127.0.0.1` 監聽，啟動時產生隨機工作階段 token，並在一般瀏覽器開啟含 token 的網址。它不提供 LAN 或遠端服務，也不會上傳 PDF、經文或核對紀錄。從本技能目錄執行：

```text
python scripts/review_cuv_index.py --data-dir <私有資料目錄> --port 0
```

若不希望自動開啟瀏覽器，加 `--no-open`。外部版本可重複提供 `--source-pdf`，或以 `COOL_BIBLE_TUTOR_SOURCE_PDFS` 提供完整路徑；Windows 使用分號、POSIX 使用冒號分隔。明確參數優先於環境變數，環境變數優先於內附 PDF。每個 PDF 的檔名和 SHA-256 必須符合資料庫紀錄，否則工具拒絕啟動。

只有人親自比對畫面所示 PDF 才能核實內容；RAG、OCR 信心、模型記憶或既有索引**不可自動核實**。第一次修改前會建立 `<私有資料目錄>/backups/cuv-before-review-<UTC>.sqlite3`。每次動作另記於 `<私有資料目錄>/cuv-review-history.sqlite3`。核實整頁需要明確輸入確認文字，而且只涵蓋同一來源頁、畫面已載入且載入後沒有變動的完整列集合。舊分頁若嘗試覆寫較新的資料，服務回覆 conflict 並保留尚未儲存的輸入。

若需手動還原：先停止核對服務，把目前 `cuv.sqlite3` 另存，再以選定的 session backup 取代它；接著重新執行 `verify_cuv_index.py`。任何核對修改都會把 RAG 標成 stale。

若只改變核實狀態，且使用 JSON 向量後端，工作台的「同步核實資料」會先取得與完整匯入共用的檔案鎖，核對上次完整匯入由實際向量檔記錄的語料結構指紋、片段數、identity digest，以及每個區塊的經文、來源頁與來源雜湊；全部一致才會備份 JSON 向量檔、原子更新 `verified_all` 與 `unverified_count`，驗證嵌入與經文未變後清除 stale。若缺少完整匯入基準，或文字、來源、結構、片段數、區塊識別、後端不符，工作台會拒絕快速同步，必須執行不帶 `--book` 或 `--chapter` 的完整匯入：

```text
python scripts/ingest_bible_rag.py --data-dir <私有資料目錄>
```

## 指定執行期資料目錄

每次查詢可傳 `--data-dir <私有資料目錄>`。也可在使用者環境設定 `COOL_BIBLE_TUTOR_DATA_DIR`；明確參數的優先級較高。若兩者皆無，程式檢查技能內的 `data/`，但可再散布安裝應使用外部可寫目錄。內附 PDF 是唯讀來源；生成的索引、核對歷史、備份與 RAG 資料都不可寫回或封裝進插件。

Windows PowerShell 與 POSIX shell 都應使用各自原生的環境變數設定方式。不要把個人絕對路徑寫入技能、manifest、測試或分享封裝。

## 選用 RAGenius 探索層

RAG 探索不是精確引文的必要條件。若要讓主題式問題先找到候選經文，請另外安裝 RAGenius，並在使用者環境設定：

```text
COOL_BIBLE_TUTOR_RAG_ROOT=<包含 rag_subsystem 的 RAGenius 根目錄>
COOL_BIBLE_TUTOR_RAG_PYTHON=<已安裝 RAGenius 相依套件的 Python 執行檔>
RAG_EMBEDDING_BACKEND=local
RAG_EMBEDDING_MODEL_PATH_BGE_LARGE_ZH=<本機 bge-large-zh 模型目錄>
RAG_VECTOR_STORE_BACKEND=pgvector
RAG_VECTOR_STORE_DSN=<使用者自己的 pgvector DSN>
```

也可依 RAGenius 文件選擇持久化 `json` backend 並設定 `RAG_VECTOR_STORE_PATH`。`in_memory` 與 `RAG_EMBEDDING_BACKEND=hash` 只供測試；正式中文探索使用本機 `bge-large-zh`。

先將私有索引匯入固定的 `cool-bible-tutor` namespace，再測試探索：

```text
python scripts/ingest_bible_rag.py --data-dir <私有資料目錄>
python scripts/discover_bible_references.py --query "饒恕與恩典" --data-dir <私有資料目錄> --top-k 5
```

兩個命令都只輸出 JSON：退出碼 0 表示成功，2 表示參數或私有語料錯誤，4 表示 RAG runtime、embedding 或 vector store 不可用。探索輸出只提供候選引用與信任／來源狀態；選中的引用仍須交給 `get_passage.py`，且只有後者退出碼 0 才是已核實精確和合本引文。
