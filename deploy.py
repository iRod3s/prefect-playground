from prefect import Flow, deploy
from prefect.deployments.runner import RunnerDeployment

from typer import Typer

from flows.example_flow import example
from flows.polars_based_flow import polars_flow
from dataclasses import dataclass, field


@dataclass
class DeploymentDefinition:
    name: str
    flow_object: Flow
    work_pool_name: str
    image: str
    extra_pip_packages: list[str] = field(default_factory=list)

    def to_deployment(self) -> RunnerDeployment:
        return self.flow_object.to_deployment(
            self.name,
            job_variables={
                "env": {"EXTRA_PIP_PACKAGES": f"{','.join(self.extra_pip_packages)}"}
            },
        )


REGISTERED_FLOWS: list[DeploymentDefinition] = [
    DeploymentDefinition(
        name="test_flow",
        flow_object=example.example_flow,
        work_pool_name="test-docker",
        image="prefect_test:dev",
    ),
    DeploymentDefinition(
        name="polars_flow",
        flow_object=polars_flow.polars_flow,
        work_pool_name="test-docker",
        image="prefect_test:dev",
        extra_pip_packages=["polars==1.22.0"],
    ),
]

app = Typer()


@app.command(name="deploy")
def deploy_flows() -> None:
    for target_flow in REGISTERED_FLOWS:
        deployment_id = deploy(
            target_flow.to_deployment(),
            work_pool_name=target_flow.work_pool_name,
            image=target_flow.image,
            push=False,
        )

        print(f"Deployed ID: {deployment_id} (Flow: {target_flow.name})")


if __name__ == "__main__":
    app()
