# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- ## Types of changes

  - **Added**: New features.
  - **Changed**: Modifications to existing functionality.
  - **Deprecated**: Features that will be removed in the future.
  - **Removed**: Features that have been removed.
  - **Fixed**: Bug fixes.
  - **Security**: Addressed vulnerabilities.

---

## [Unreleased RPC]

## [Unreleased]

### Added

- **Add socket client validation**: verify if client socket is in agent database.
- **Create agent wake ping handler**: write agent server wake ping handler.
- **Create agent wake ping service**: write agent server wake ping service.
- **Create Agents management api**: build an agent service management backent.
- **Create simple server**: create a simple api server with fastapi.
- **Refactor codebase**: re-structure code to fit HSMS architecture.
- **Create a simple socket server**: setup a websocket server.
- **Extent .gitignore**: use public python .gitignore template.
- **Initialize repository**: set up project structure with initial files.

### Changed

- **Improve code style**: make agent service and handler more predictable.
- **Add agent UUID to header**: extent wake_ping request header with agent uuid.
- **Re-word wake_url to ping_url**: re-word wake_url ro ping url.

### Fixed

- **Bug fixes**: update agent model, agent schema, agent service and handler.
- **fixed ping request header**: send uuid in header instead of uuid dict.

[unreleased RPC]: https://github.com/kyprware/synapse/compare/main
[unreleased]: https://github.com/kyprware/synapse/compare/main
