# Changelog

All notable changes to preflight are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-05-28

### Added
- CLI entry point (`preflight <path>`) with `--json`, `--quiet`, `--no-color`, and `--version` flags.
- Language detection by file extension for Python, JavaScript, TypeScript, Go, Rust, Java, Kotlin, Ruby, PHP, C#, C, C++, Swift, Scala, Shell, Lua, R, Dart, Elixir, Erlang, Zig, Nim, and Perl.
- Non-blank line counting per language.
- Package manager detection from manifest files (requirements.txt, pyproject.toml, package.json, go.mod, Cargo.toml, composer.json, Gemfile, pom.xml, build.gradle, and more).
- Dependency name extraction for Python (requirements.txt, pyproject.toml), Node (package.json), Go (go.mod), Rust (Cargo.toml), and PHP (composer.json).
- Environment variable extraction via regex for Python, JavaScript, TypeScript, Go, Ruby, Rust, and PHP source files.
- Parsing of .env, .env.example, .env.sample, and .env.template files for defined variable names.
- Docker Compose service parsing with image and port extraction (supports docker-compose.yml and compose.yml).
- Dockerfile EXPOSE directive detection.
- Procfile process type detection.
- Port binding detection from source code patterns including Go address literals.
- Well-known port labeling (PostgreSQL, Redis, MySQL, MongoDB, Kafka, Elasticsearch, and others).
- Rich terminal output with summary panel, tables, and dependency sorting.
- JSON output mode with summary statistics.
- Quiet output mode for single-line summaries.
- ProjectReport summary properties (total_files, total_lines, total_dependencies, required_env_vars).
- Test suite with fixture projects (Python, Node, Docker, Go, Rust) and unit tests for all modules.
