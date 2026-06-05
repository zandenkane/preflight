# preflight

![CI](https://github.com/zandenkane/preflight/actions/workflows/ci.yml/badge.svg)

clone a repo. try to run it. it needs Redis. and Postgres. and 14 environment variables, 3 of which are not documented anywhere. spend the next 3 hours reading Dockerfiles and grepping for os.environ. question your career choices.

preflight skips all of that. point it at any project directory and it tells you everything you need to run it. languages, package managers, dependencies, env vars, services, ports. one command, done.

No more reading through 6 config files and a half-written README just to find out the app needs Node 18 and a `.env` with `SECRET_KEY` in it.

## Install

```bash
pip install .
```

For hacking on it:

```bash
pip install -e ".[dev]"
```

Python 3.10+.

## Usage

```bash
# scan whatever directory you're staring at
preflight .

# scan something specific
preflight /path/to/that/repo/you/just/cloned

# json output so you can pipe it into whatever
preflight . --json

# just the summary, nothing else
preflight . --quiet

# no colors if your terminal is weird about it
preflight . --no-color

# check the version
preflight --version
```

## What it finds

**Languages** - Counts source files and lines of code by extension. Python, JavaScript, TypeScript, Go, Rust, Java, Kotlin, Ruby, PHP, C#, C, C++, Swift, Scala, Shell, Lua, R, Dart, Elixir, Erlang, Zig, Nim, Perl.

**Package managers and dependencies** - Spots manifest files (requirements.txt, package.json, go.mod, Cargo.toml, composer.json, pyproject.toml, and a bunch more) and actually parses out the dependency names where it can. For the rest it at least tells you the package manager exists.

**Environment variables** - Scans source code with regex patterns for `os.getenv()`, `process.env.`, `os.Getenv()`, `ENV[]`, `env::var()`, `getenv()`, and friends. Also reads `.env`, `.env.example`, `.env.sample`, and `.env.template` files. Tells you which vars have defaults and which ones will blow up if they are missing.

**Services** - Parses docker-compose.yml (or compose.yml) for service definitions with images and ports. Picks up Dockerfile EXPOSE directives. Reads Procfile for process types.

**Ports** - Finds port bindings in source code (`.listen()`, `.bind()`, port variable assignments, Go address literals). Combines those with ports from Docker config. Labels the well known ones (5432 = PostgreSQL, 6379 = Redis, 3306 = MySQL, you get the idea).

## Example

```bash
$ preflight ./myapp --json | jq '.summary'
{
  "path": "/home/user/myapp",
  "languages_found": 1,
  "total_source_files": 6,
  "total_source_lines": 340,
  "package_managers_found": 1,
  "total_dependencies": 4,
  "env_vars_found": 4,
  "required_env_vars": 1,
  "services_found": 0,
  "ports_found": 1
}
```

That is 4 seconds instead of 40 minutes of reading.

## License

MIT. See [LICENSE](LICENSE).
