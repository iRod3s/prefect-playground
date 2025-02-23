from typer import Typer

from uuid import UUID
from deploy import deploy_flows

from prefect import get_client

from blocks.s3_default_block import register_blocks as register_s3_blocks

import json

app = Typer()


@app.command(name="deploy")
def run_deployment() -> None:
    deploy_flows()


@app.command(name="register_blocks")
def register_blocks() -> None:
    register_s3_blocks()


@app.command(name="trigger_flow")
def trigger_flow(deployment_id: UUID, params_json: str) -> None:
    parsed_params = json.loads(params_json)

    with get_client(sync_client=True) as client:
        created_flow_run = client.create_flow_run_from_deployment(
            deployment_id=deployment_id, parameters=parsed_params
        )
        print(f"Flow run created. ID = {created_flow_run.id}")


if __name__ == "__main__":
    app()
