"""Tests for the data model classes."""

from preflight.models import (
    EnvVar,
    Language,
    PackageManager,
    Port,
    ProjectReport,
    Service,
)


def test_language_to_dict():
    lang = Language(name="Python", extension=".py", file_count=10, line_count=500)
    d = lang.to_dict()
    assert d["name"] == "Python"
    assert d["extension"] == ".py"
    assert d["file_count"] == 10
    assert d["line_count"] == 500


def test_language_default_line_count():
    lang = Language(name="Go", extension=".go", file_count=3)
    assert lang.line_count == 0


def test_package_manager_dependency_count():
    pm = PackageManager(
        name="pip", manifest_file="requirements.txt",
        dependencies=["flask", "redis"],
    )
    assert pm.dependency_count == 2


def test_package_manager_empty_deps():
    pm = PackageManager(name="cargo", manifest_file="Cargo.toml")
    assert pm.dependency_count == 0
    assert pm.to_dict()["dependency_count"] == 0


def test_envvar_required_property():
    required = EnvVar(name="SECRET_KEY", source_file="app.py", has_default=False)
    optional = EnvVar(name="DEBUG", source_file="app.py", has_default=True)
    assert required.required is True
    assert optional.required is False


def test_envvar_to_dict_includes_required():
    var = EnvVar(name="PORT", source_file="app.py", has_default=True)
    d = var.to_dict()
    assert "required" in d
    assert d["required"] is False


def test_service_to_dict():
    svc = Service(name="web", image="nginx:latest", ports=["80:80"], source="docker-compose")
    d = svc.to_dict()
    assert d["name"] == "web"
    assert d["ports"] == ["80:80"]


def test_port_to_dict():
    p = Port(number=5432, label="PostgreSQL", source="docker-compose")
    d = p.to_dict()
    assert d["number"] == 5432
    assert d["label"] == "PostgreSQL"


def test_report_total_files():
    report = ProjectReport(
        path="/tmp/test",
        languages=[
            Language(name="Python", extension=".py", file_count=5),
            Language(name="JavaScript", extension=".js", file_count=3),
        ],
    )
    assert report.total_files == 8


def test_report_total_lines():
    report = ProjectReport(
        path="/tmp/test",
        languages=[
            Language(name="Python", extension=".py", file_count=5, line_count=200),
            Language(name="Go", extension=".go", file_count=2, line_count=100),
        ],
    )
    assert report.total_lines == 300


def test_report_total_dependencies():
    report = ProjectReport(
        path="/tmp/test",
        package_managers=[
            PackageManager(name="pip", manifest_file="requirements.txt", dependencies=["flask"]),
            PackageManager(
                name="npm", manifest_file="package.json",
                dependencies=["express", "cors"],
            ),
        ],
    )
    assert report.total_dependencies == 3


def test_report_required_env_vars():
    report = ProjectReport(
        path="/tmp/test",
        env_vars=[
            EnvVar(name="SECRET_KEY", source_file="app.py", has_default=False),
            EnvVar(name="DEBUG", source_file="app.py", has_default=True),
            EnvVar(name="API_KEY", source_file="app.py", has_default=False),
        ],
    )
    req = report.required_env_vars
    assert len(req) == 2
    names = {v.name for v in req}
    assert "SECRET_KEY" in names
    assert "API_KEY" in names


def test_report_is_empty():
    empty = ProjectReport(path="/tmp/test")
    assert empty.is_empty is True

    non_empty = ProjectReport(
        path="/tmp/test",
        languages=[Language(name="Python", extension=".py", file_count=1)],
    )
    assert non_empty.is_empty is False


def test_report_summary():
    report = ProjectReport(
        path="/tmp/test",
        languages=[Language(name="Python", extension=".py", file_count=5, line_count=200)],
        package_managers=[
            PackageManager(
                name="pip", manifest_file="requirements.txt",
                dependencies=["flask"],
            ),
        ],
        env_vars=[
            EnvVar(name="KEY", source_file="app.py", has_default=False),
            EnvVar(name="DEBUG", source_file="app.py", has_default=True),
        ],
    )
    s = report.summary()
    assert s["languages_found"] == 1
    assert s["total_source_files"] == 5
    assert s["total_source_lines"] == 200
    assert s["total_dependencies"] == 1
    assert s["env_vars_found"] == 2
    assert s["required_env_vars"] == 1


def test_report_to_dict_has_summary():
    report = ProjectReport(path="/tmp/test")
    d = report.to_dict()
    assert "summary" in d
    assert d["summary"]["languages_found"] == 0
