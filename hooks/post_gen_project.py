"""Post-generation hook for cookiecutter template."""

import os
import shutil

USE_DOCKER = "{{ cookiecutter.use_docker }}" == "True"

DOCKER_FILES = [
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.dev.yml",
    "docker-compose.test.yml",
    "docker-compose.prod.yml",
]


def remove_file(filepath: str) -> None:
    """Remove a file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)


def main() -> None:
    if not USE_DOCKER:
        for filename in DOCKER_FILES:
            remove_file(filename)
        print("\nDocker files removed (use_docker=false).")
        print("\nQuickstart:")
        print("  uv sync        # or: pip install -e '.[dev]'")
        print("  uvicorn app.main:app --reload")
    else:
        print("\nQuickstart:")
        print("  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up")

    print(f"\nService will be available at http://localhost:8000/health")


if __name__ == "__main__":
    main()
