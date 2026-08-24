# Privacy

Cool Bible Tutor performs exact Scripture retrieval and semantic discovery locally. The bundled corpus and compact index are read-only. Topic queries, selected references, study answers, and review activity are not sent to the publisher.

`setup-rag` performs network access only after explicit consent. It contacts the Python package indexes listed in `vendor/rag-runtime/runtime-lock.json` and the immutable HTTPS model-file URLs listed in `vendor/rag-runtime/model-manifest.json`. It sends ordinary package/model download requests; it does not send Bible-study queries.

The managed runtime, model, and configuration are stored in the operating system's per-user application-data directory under `ObviousOne/cool-bible-tutor`. `config.json` contains only runtime paths, versions, digests, and a completion timestamp. It contains no credentials or prompts.

Optional authoring/review data, OCR output, corrections, review history, backups, and private vector stores stay outside the plugin and are never included by the marketplace release builder.
