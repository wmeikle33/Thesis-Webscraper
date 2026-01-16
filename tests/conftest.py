from pathlib import Path
import pytest

@pytest.fixture
def load_fixture():
    def _load(name: str) -> str:
        path = Path(__file__).parent / "fixtures" / name
        return path.read_text(encoding="utf-8")
    return _load
