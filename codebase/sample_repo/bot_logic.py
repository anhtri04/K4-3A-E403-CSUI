"""BuildMate team helper — sample repo for explain demo."""

def buildmate_propose_diff(task: str) -> dict:
    """Propose a branch-only diff for review. Never pushes to main."""
    return {"patch": f"# TODO: {task}", "branch": "buildmate/proposal"}


def validate_input(s: str) -> bool:
    return bool(s and len(s.strip()) > 0)
