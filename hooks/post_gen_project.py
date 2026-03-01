"""Post-generation hook for cookiecutter template."""

import os
import shutil

USE_DOCKER = "{{ cookiecutter.use_docker }}" == "True"

ENV_DIRS = ["deploy/local", "deploy/dev", "deploy/stage", "deploy/prod"]


def _generate_env_files() -> None:
    """Copy each .env.*.example to .env.* so docker-compose can find them."""
    for env_dir in ENV_DIRS:
        if not os.path.isdir(env_dir):
            continue
        for filename in os.listdir(env_dir):
            if filename.endswith(".example"):
                src = os.path.join(env_dir, filename)
                dst = os.path.join(env_dir, filename[: -len(".example")])
                if not os.path.exists(dst):
                    shutil.copy(src, dst)


def main() -> None:
    if not USE_DOCKER:
        if os.path.exists("deploy"):
            shutil.rmtree("deploy")
        print("\nDocker files removed (use_docker=false).")
        print("\nQuickstart:")
        print("  uv sync        # or: pip install -e '.[dev]'")
        print("  uvicorn app.main:app --reload")
    else:
        _generate_env_files()
        print("\nQuickstart:")
        print("  cd deploy/local && docker-compose up")
        print("\nOther environments:")
        print("  cd deploy/dev   && docker-compose up")
        print("  cd deploy/stage && docker-compose up")
        print("  cd deploy/prod  && docker-compose up")

    print("\nService will be available at http://localhost:8000/health")


if __name__ == "__main__":
    main()
