# Refactor Plan: Synapse Python Server

## Goals
- Use a structured architecture: Handler + Service + Model + Socket App
- Improve modularity and maintainability
- Align with best practices for scalable Python server code

## Target Structure
- `handlers/`: Route events or requests
- `services/`: Business logic layer
- `models/`: Data definitions
- `core/`: Socket app + config
- `utils/`: Shared helpers

## Steps
1. Move existing code into new folders
2. Rename files to match roles
3. Create app.py entry point
4. Refactor socket logic into core/socket_app.py
5. Ensure all tests pass
6. Remove obsolete files and clean up
