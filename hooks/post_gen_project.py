"""Post-generation hook for cookiecutter template."""

import os
import shutil

USE_DOCKER = "{{ cookiecutter.use_docker }}" == "True"


def main() -> None:
    if not USE_DOCKER:
        if os.path.exists("deploy"):
            shutil.rmtree("deploy")
        print("\nDocker files removed (use_docker=false).")
        print("\nQuickstart:")
        print("  uv sync        # or: pip install -e '.[dev]'")
        print("  uvicorn app.main:app --reload")
    else:
        print("\nQuickstart:")
        print("  cd deploy/local && docker-compose up")
        print("\nOther environments:")
        print("  cd deploy/dev   && docker-compose up")
        print("  cd deploy/stage && docker-compose up")
        print("  cd deploy/prod  && docker-compose up")

    print("\nService will be available at http://localhost:8000/health")


if __name__ == "__main__":
    main()
