# contributing

Want to add detection for a new language or package manager? Add a detector under src/preflight/detectors/ and register it in __init__.py. Each detector is a function that takes a project path and returns findings.

`pip install -e .[dev]` then `pytest` to verify everything works.
