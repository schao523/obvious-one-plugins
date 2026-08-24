# Security

Please report suspected vulnerabilities privately to the repository owner before public disclosure. Include the affected tag, operating system, reproduction steps, and non-sensitive logs.

Every pull request runs the plugin tests and distribution audit on Windows, Linux, and macOS without downloading the embedding model. A separate manually approved workflow exercises the heavyweight managed-RAG setup and offline Traditional Chinese smoke query.

Release tags must be built from the allowlisted marketplace builder. Do not commit credentials, private review/authoring data, model weights, writable vector stores, caches, or machine-specific configuration.
