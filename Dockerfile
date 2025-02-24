FROM prefecthq/prefect:3.1.14-python3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml /opt/prefect/workspace/pyproject.toml
COPY uv.lock /opt/prefect/workspace/uv.lock
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --frozen --directory /opt/prefect/workspace
COPY . /opt/prefect/workspace/
WORKDIR /opt/prefect/workspace/
