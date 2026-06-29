from __future__ import annotations


COMMANDS = [
    "validate",
    "v",
    "guide",
    "g",
    "maintainer-packet",
    "mp",
    "explain",
    "doctor",
    "rules",
    "pull-request",
    "pr",
    "draft",
    "d",
    "docs",
    "cli",
    "init",
    "completion",
]

OPTIONS = [
    "--help",
    "--version",
    "--repo",
    "--base",
    "--ai",
    "--ai-assisted",
    "--human",
    "--human-authored",
    "--body-file",
    "--evidence",
    "--evidence-file",
    "--output",
    "--format",
    "--annotations",
    "--run-checks",
    "--skip-checks",
    "--title",
    "--base-branch",
    "--head-branch",
    "--write",
    "--check",
    "--path",
    "--force",
    "--no-body",
]


def render_completion(shell: str) -> str:
    if shell == "bash":
        return render_bash()
    if shell == "zsh":
        return render_zsh()
    if shell == "fish":
        return render_fish()
    raise ValueError(f"unsupported shell: {shell}")


def render_bash() -> str:
    words = " ".join(COMMANDS + OPTIONS)
    return f"""# bash completion for themis
_themis_complete() {{
  local cur="${{COMP_WORDS[COMP_CWORD]}}"
  COMPREPLY=( $(compgen -W "{words}" -- "$cur") )
}}
complete -F _themis_complete themis
"""


def render_zsh() -> str:
    words = " ".join(COMMANDS + OPTIONS)
    return f"""#compdef themis
_themis() {{
  compadd -- {words}
}}
_themis "$@"
"""


def render_fish() -> str:
    lines = ["# fish completion for themis"]
    for word in COMMANDS:
        lines.append(f"complete -c themis -f -a {word}")
    for option in OPTIONS:
        lines.append(f"complete -c themis -f -l {option.removeprefix('--')}")
    return "\n".join(lines) + "\n"
