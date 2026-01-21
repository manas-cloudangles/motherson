# Legacy Backend Code

This directory contains the original monolithic backend code that has been refactored into the `app/` directory.
These files are kept for reference but should not be used in the new architecture.

## Refactoring Mapping

- `api_server.py` -> `app/main.py` and `app/api/`
- `config.py` -> `app/core/config.py`
- `get_secrets.py` -> `app/core/secrets.py` and `app/services/llm_service.py`
- `component_metadata_pipeline.py` & `component_selector.py` -> `app/services/metadata_service.py`
- `page_generation_pipeline.py` -> `app/services/generation_service.py`
- `workspace_state.py` -> `app/services/workspace_service.py`
- `utils.py` -> `app/utils/parsers.py`
