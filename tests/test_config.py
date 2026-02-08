"""Test configuration."""
import os
from pathlib import Path


def test_project_structure():
    """Test that all important files exist."""
    project_root = Path(__file__).parent.parent

    important_files = [
        "pyproject.toml",
        "README.md",
        ".env.example",
        "src/main.py",
        "src/config.py",
        "src/core/models.py",
        "src/core/schemas.py",
        "src/core/database.py",
        "src/ai/parser.py",
        "src/ai/providers.py",
        "src/services/record_service.py",
        "src/cli/finance.py",
        "src/cli/health.py",
        "src/cli/work.py",
        "src/cli/leisure.py",
        "src/cli/report.py",
        "prompts/parse_finance.txt",
        "prompts/parse_health.txt",
        "prompts/parse_work.txt",
        "prompts/parse_leisure.txt",
    ]

    for file_path in important_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Missing file: {file_path}"

    print("[OK] All project files exist")


def test_config_loading():
    """Test that configuration can be loaded."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        from src.config import settings
        assert hasattr(settings, "ai_provider")
        assert hasattr(settings, "database_url")
        print("[OK] Configuration loads successfully")
    except Exception as e:
        print(f"[FAIL] Configuration loading failed: {e}")
        raise


if __name__ == "__main__":
    test_project_structure()
    test_config_loading()
    print("\n[OK] All basic tests passed!")
