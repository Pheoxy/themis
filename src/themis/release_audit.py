from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import subprocess


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


SECRET_PATTERNS = {
    "private-key-block": re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "openai-token": re.compile(r"sk-[A-Za-z0-9]{32,}"),
    "anthropic-token": re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    "npm-token": re.compile(r"npm_[A-Za-z0-9]{20,}"),
    "slack-token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "stripe-live-secret": re.compile(r"sk_live_[A-Za-z0-9]{20,}"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "generic-secret-assignment": re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|credential)\s*[:=]\s*[\"']?[^\"'\s]{16,}[\"']?"
    ),
}
GIT_SECRET_PATTERNS = {
    "private-key-block": (r"-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", False),
    "aws-access-key": (r"AKIA[0-9A-Z]{16}", False),
    "github-token": (r"gh[pousr]_[A-Za-z0-9_]{20,}", False),
    "openai-token": (r"sk-[A-Za-z0-9]{32,}", False),
    "anthropic-token": (r"sk-ant-[A-Za-z0-9_-]{20,}", False),
    "npm-token": (r"npm_[A-Za-z0-9]{20,}", False),
    "slack-token": (r"xox[baprs]-[A-Za-z0-9-]{20,}", False),
    "stripe-live-secret": (r"sk_live_[A-Za-z0-9]{20,}", False),
    "jwt": (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", False),
    "generic-secret-assignment": (
        r"(^|[^[:alnum:]_])(api[_-]?key|secret|token|password|credential)[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{16,}[\"']?",
        True,
    ),
}
TEMPLATE_RE = re.compile(r"OWNER/themis|example\.com")
GENERATED_TRACKED_RE = re.compile(r"(^|/)(__pycache__/|\.pytest_cache/|\.ruff_cache/|\.mypy_cache/|dist/|build/|.*\.py[co]$|\.env(\..*)?$)")
LARGE_ASSET_BYTES = 1_000_000


@dataclass(frozen=True)
class AuditCheck:
    status: str
    code: str
    message: str
    detail: str | None = None


@dataclass(frozen=True)
class AuditResult:
    repo: Path
    checks: list[AuditCheck]


@dataclass(frozen=True)
class SecretHit:
    pattern: str
    path: str
    line: int


def inspect_release_audit(repo: Path, *, include_history: bool = False) -> AuditResult:
    checks = [
        license_check(repo),
        tracked_generated_check(repo),
        template_reference_check(repo),
        asset_provenance_check(repo),
        asset_size_check(repo),
        current_secret_check(repo),
    ]
    if include_history:
        checks.append(history_secret_check(repo))
    return AuditResult(repo=repo, checks=checks)


def audit_exit_code(result: AuditResult) -> int:
    return 2 if any(check.status == FAIL for check in result.checks) else 0


def license_check(repo: Path) -> AuditCheck:
    license_file = repo / "LICENSE"
    pyproject = repo / "pyproject.toml"
    if not license_file.exists() or not license_file.read_text(encoding="utf-8", errors="replace").strip():
        return AuditCheck(FAIL, "license-file", "LICENSE is missing or empty.")
    if not pyproject.exists() or "Apache-2.0" not in pyproject.read_text(encoding="utf-8", errors="replace"):
        return AuditCheck(FAIL, "package-license", "Package metadata does not declare the Apache-2.0 license.")
    return AuditCheck(PASS, "license", "LICENSE and package license metadata are present.")


def tracked_generated_check(repo: Path) -> AuditCheck:
    generated = [path for path in tracked_files(repo) if GENERATED_TRACKED_RE.search(path)]
    if generated:
        return AuditCheck(FAIL, "tracked-generated-files", "Generated/cache files are tracked.", summarize(generated))
    return AuditCheck(PASS, "tracked-generated-files", "No generated/cache files are tracked.")


def template_reference_check(repo: Path) -> AuditCheck:
    hits: list[str] = []
    for path in tracked_files(repo):
        if path.startswith("tests/") or path in {"src/themis/release_audit.py", "src/themis/version_check.py"}:
            continue
        for line_no, line in text_lines(repo / path):
            if TEMPLATE_RE.search(line):
                hits.append(f"{path}:{line_no}")
    if hits:
        return AuditCheck(FAIL, "template-references", "Release-facing files still contain template repository URLs.", summarize(hits))
    return AuditCheck(PASS, "template-references", "No release-facing template repository URLs found.")


def asset_provenance_check(repo: Path) -> AuditCheck:
    assets = [path for path in tracked_files(repo) if path.startswith("docs/assets/") and path.endswith(".png")]
    if not assets:
        return AuditCheck(PASS, "asset-provenance", "No tracked raster assets found.")
    provenance = repo / "docs" / "assets" / "PROVENANCE.md"
    if not provenance.exists() or not provenance.read_text(encoding="utf-8", errors="replace").strip():
        return AuditCheck(FAIL, "asset-provenance", "Tracked raster assets need explicit provenance and licensing before 1.0.", summarize(assets))
    provenance_text = provenance.read_text(encoding="utf-8", errors="replace")
    required_terms = ["Chat" + "GPT", "Open" + "AI", "Apache License", "not represented as human-created"]
    missing = [term for term in required_terms if term not in provenance_text]
    if missing:
        return AuditCheck(FAIL, "asset-provenance", "Asset provenance is missing required AI-generation or licensing disclosures.", summarize(missing))
    return AuditCheck(PASS, "asset-provenance", "Tracked raster assets have provenance documentation.")


def asset_size_check(repo: Path) -> AuditCheck:
    assets = [path for path in tracked_files(repo) if path.startswith("docs/assets/") and path.endswith(".png")]
    large = [path for path in assets if (repo / path).exists() and (repo / path).stat().st_size > LARGE_ASSET_BYTES]
    if not large:
        return AuditCheck(PASS, "asset-size", "No tracked raster assets exceed the large-asset threshold.")
    approved = approved_large_assets(repo)
    unapproved = [path for path in large if path not in approved]
    if unapproved:
        return AuditCheck(
            WARN,
            "asset-size",
            "Tracked raster assets exceed the large-asset threshold and are not documented as approved.",
            summarize(unapproved),
        )
    return AuditCheck(PASS, "asset-size", "Large tracked raster assets are explicitly approved in provenance documentation.")


def approved_large_assets(repo: Path) -> set[str]:
    provenance = repo / "docs" / "assets" / "PROVENANCE.md"
    if not provenance.exists():
        return set()
    text = provenance.read_text(encoding="utf-8", errors="replace")
    section = re.search(r"(?ms)^## Approved Large Raster Assets\n(?P<body>.*?)(?:\n## |\Z)", text)
    if not section:
        return set()
    return set(re.findall(r"`(docs/assets/[^`]+\.png)`", section.group("body")))


def current_secret_check(repo: Path) -> AuditCheck:
    hits = scan_files_for_secrets(repo, tracked_files(repo))
    real_hits = [hit for hit in hits if not is_synthetic_secret_fixture(hit)]
    synthetic = [hit for hit in hits if is_synthetic_secret_fixture(hit)]
    if real_hits:
        return AuditCheck(FAIL, "tracked-secret-patterns", "Tracked files contain secret-like values. Values are not printed.", summarize_hits(real_hits))
    if synthetic:
        return AuditCheck(WARN, "tracked-secret-fixtures", "Only synthetic redaction fixtures matched secret-like patterns.", summarize_hits(synthetic))
    return AuditCheck(PASS, "tracked-secret-patterns", "No tracked secret-like values found.")


def history_secret_check(repo: Path) -> AuditCheck:
    hits: list[SecretHit] = []
    try:
        commits = git(repo, "rev-list", "--all").splitlines()
    except subprocess.CalledProcessError:
        return AuditCheck(FAIL, "history-secret-scan", "Git history audit requires a git repository.")
    for commit in commits:
        for pattern_name, (pattern, ignore_case) in GIT_SECRET_PATTERNS.items():
            command = ["git", "grep", "-I", "-n", "-E"]
            if ignore_case:
                command.append("-i")
            command.extend(["-e", pattern, commit, "--", "."])
            completed = subprocess.run(
                command,
                cwd=repo,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if completed.returncode == 1:
                continue
            if completed.returncode != 0:
                return AuditCheck(FAIL, "history-secret-scan", f"Git history secret scan failed at {commit[:12]}.")
            for line in completed.stdout.splitlines():
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    _, path, line_no, _ = parts
                    hits.append(SecretHit(pattern_name, path, int(line_no)))
    real_hits = [hit for hit in hits if not is_synthetic_secret_fixture(hit)]
    synthetic = [hit for hit in hits if is_synthetic_secret_fixture(hit)]
    if real_hits:
        return AuditCheck(FAIL, "history-secret-patterns", "Git history contains secret-like values. Values are not printed.", summarize_hits(real_hits))
    if synthetic:
        return AuditCheck(WARN, "history-secret-fixtures", "Git history contains only synthetic redaction fixtures matching secret-like patterns.", summarize_hits(synthetic))
    return AuditCheck(PASS, "history-secret-patterns", "No secret-like values found in reachable git history.")


def scan_files_for_secrets(repo: Path, paths: list[str]) -> list[SecretHit]:
    hits: list[SecretHit] = []
    for path in paths:
        target = repo / path
        try:
            data = target.read_bytes()
        except OSError:
            continue
        if b"\0" in data:
            continue
        for line_no, line in text_lines(target):
            for pattern_name, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    hits.append(SecretHit(pattern_name, path, line_no))
    return hits


def is_synthetic_secret_fixture(hit: SecretHit) -> bool:
    return hit.path == "tests/test_providers.py" and hit.line in {122, 130, 141}


def tracked_files(repo: Path) -> list[str]:
    try:
        return [item for item in git(repo, "ls-files", "-z").split("\0") if item]
    except subprocess.CalledProcessError:
        output: list[str] = []
        for path in repo.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(repo).as_posix()
            parts = set(relative.split("/"))
            if (
                relative.startswith(".git/")
                or "/.git/" in relative
                or parts & {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "build", "dist"}
                or any(part.endswith(".egg-info") for part in parts)
            ):
                continue
            output.append(relative)
        return sorted(output)


def text_lines(path: Path) -> list[tuple[int, str]]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if b"\0" in data:
        return []
    return list(enumerate(data.decode("utf-8", errors="replace").splitlines(), 1))


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True)


def summarize(values: list[str], *, limit: int = 12) -> str:
    shown = values[:limit]
    suffix = f"; +{len(values) - limit} more" if len(values) > limit else ""
    return "; ".join(shown) + suffix


def summarize_hits(hits: list[SecretHit]) -> str:
    values = sorted({f"{hit.pattern}:{hit.path}:{hit.line}" for hit in hits})
    return summarize(values)


def render_audit_markdown(result: AuditResult) -> str:
    status = "BLOCKED" if audit_exit_code(result) else "PASS"
    lines = [
        "# Themis Release Audit",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{result.repo}`",
        "",
        "## Checks",
        "",
    ]
    for check in result.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
        if check.detail:
            lines.append(f"  Detail: `{check.detail}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit is a deterministic release-readiness check. It is not legal advice and cannot prove absence of infringement or undiscovered secrets.",
            "",
        ]
    )
    return "\n".join(lines)


def render_audit_json(result: AuditResult) -> str:
    payload = {
        "tool": "themis",
        "workflow": "release audit",
        "status": "blocked" if audit_exit_code(result) else "pass",
        "exit_code": audit_exit_code(result),
        "repository": str(result.repo),
        "checks": [asdict(check) for check in result.checks],
        "boundary": "deterministic release-readiness check; not legal advice",
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
