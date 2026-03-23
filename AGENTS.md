# Repository Guidelines

## Project Structure & Module Organization
This project is a desktop PDF-to-Excel extractor organized with Clean Architecture. `main.py` boots the ttkbootstrap GUI. `src/domain/` contains models, constants, errors, and pure business services. `src/app/use_cases/` coordinates extraction and export flows. `src/infrastructure/` holds adapters for PDF parsing, Excel generation, and JSON-backed territory data. `src/presentation/gui/` contains the window, views, controllers, and widgets. Keep design notes in `conductor/`. Use `data/` only for local PDFs, config, and generated spreadsheets; it is gitignored.

## Build, Test, and Development Commands
- `uv sync` — install the locked Python 3.13 dependencies from `uv.lock`.
- `uv sync --locked` — install only runtime dependencies before packaging with PyInstaller.
- `uv run python main.py` — launch the GUI locally.
- `uv run ruff check .` — run the code-quality gate used by CI before building or opening a PR.
- `uv run pytest` — run the current unit-test suite.
- `uv run --with pyinstaller python scripts/build_pyinstaller.py` — build the desktop executable with PyInstaller without adding permanent packaging dependencies to the project.
- `uv run python -m compileall src main.py` — run a fast syntax check before opening a PR.
- `uv lock` — refresh the lockfile after changing runtime dependencies in `pyproject.toml`.

## Coding Style & Naming Conventions
Use 4-space indentation and follow standard Python/PEP 8 spacing. Prefer small, single-purpose classes and keep imports explicit. File and module names use `snake_case.py`; classes use `PascalCase`; interfaces keep the existing `I...` prefix (for example, `IPDFExtractor`). Preserve layer boundaries: `presentation -> app -> domain`, while `infrastructure` implements domain contracts. Write code comments in Spanish to match the current codebase.

## Testing Guidelines
Create tests in a top-level `tests/` package that mirrors `src/` (example: `tests/domain/test_transform_data.py`). Prioritize unit tests for `domain` and `app`, then add focused integration tests for `PyMuPDFExtractor` and `OpenPyXLExporter`. For parser changes, validate against representative BOE PDFs and record the expected Excel columns or row count in the test case or PR notes.

GitHub Actions en `.github/workflows/` runs `ruff`, `pytest`, and the Windows PyInstaller build. Keep local and CI commands aligned.

## Commit & Pull Request Guidelines
The existing history uses Conventional Commits (`chore: migrate to uv and prepare for public repository`); continue with prefixes such as `feat:`, `fix:`, `refactor:`, and `chore:`. Keep commits focused by layer or feature. PRs should include: a short summary, affected modules, validation steps, and screenshots or GIFs for GUI changes. Link related issues when available.

## Data & Configuration Tips
`TerritoriesRepositoryJSON` reads `src/territorios_espana.json` and can download the source dataset if the file is missing. Do not commit personal PDFs, generated Excel files, or secrets. Keep temporary inputs under `data/` or another ignored path.
