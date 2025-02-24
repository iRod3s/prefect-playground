from prefect import Flow, deploy
from prefect.deployments.runner import RunnerDeployment
from prefect.docker import DockerImage

from flows.example_flow import example
from flows.polars_based_flow import polars_flow
from flows.scheduled_and_reaggs import main
from flows.multi_flow_pipeline import first_flow, second_flow, explicit_first_flow
from dataclasses import dataclass, field

from prefect.automations import Automation
from prefect.events import DeploymentEventTrigger
from prefect.automations import RunDeployment


@dataclass
class AutomationDefinition:
    name: str
    automate_after_flow_name: str


@dataclass
class DeploymentDefinition:
    name: str
    flow_object: Flow
    work_pool_name: str
    image: str
    extra_pip_packages: list[str] = field(default_factory=list)
    cron_interval: str | None = None
    automation: AutomationDefinition | None = None

    def resolve_job_variables(self) -> dict[str, str | dict[str, str]]:
        result = {}

        if self.extra_pip_packages:
            result["env"] = {
                "EXTRA_PIP_PACKAGES": f"{','.join(self.extra_pip_packages)}"
            }

        return result

    def to_deployment(self) -> RunnerDeployment:
        return self.flow_object.to_deployment(
            self.name,
            job_variables=self.resolve_job_variables(),
            cron=self.cron_interval,
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
    DeploymentDefinition(
        name="scheduled_flow",
        flow_object=main.scheduled_flow,
        work_pool_name="test-docker",
        image="prefect_test:dev",
        cron_interval="0 0 * * *",
    ),
    DeploymentDefinition(
        name="multistep_first_flow",
        flow_object=first_flow.first_flow,
        work_pool_name="test-docker",
        image="prefect_test:dev",
        cron_interval="0 0 * * *",
    ),
    DeploymentDefinition(
        name="multistep_second_flow",
        flow_object=second_flow.second_flow,
        work_pool_name="test-docker",
        image="prefect_test:dev",
        automation=AutomationDefinition(
            name="do_second_step",
            automate_after_flow_name=first_flow.first_flow.name,
        ),
    ),
    DeploymentDefinition(
        name="multistep_first_flow_explicit",
        flow_object=explicit_first_flow.first_flow_explicit,
        work_pool_name="test-docker",
        image="prefect_test:dev",
    ),
]


def deploy_flows() -> None:
    created_deployments_ids = {}

    pending_deployments = REGISTERED_FLOWS.copy()

    while len(pending_deployments) > 0:
        target_flow = pending_deployments.pop(0)
        if (
            target_flow.automation is not None
            and target_flow.automation.automate_after_flow_name
            not in created_deployments_ids
        ):
            print(
                f"Skipping {target_flow.name} because {target_flow.automation.automate_after_flow_name} is not deployed yet"
            )
            pending_deployments.append(target_flow)

        # TODO: Run all deployments at once to avoid building the same image multiple times
        deployment_id = deploy(
            target_flow.to_deployment(),
            work_pool_name=target_flow.work_pool_name,
            image=DockerImage(name=target_flow.image, dockerfile="Dockerfile"),
            # image=target_flow.image,
            push=False,
        )

        print(f"Deployed ID: {deployment_id} (Flow: {target_flow.name})")

        created_deployments_ids[target_flow.name] = deployment_id

        if target_flow.automation is not None:
            if target_flow.automation.automate_after_flow_name == target_flow.name:
                raise (ValueError("Cannot automate after itself"))

            try:
                automation: Automation = Automation.read(
                    name=target_flow.automation.name
                )
                print(
                    f"Automation already exists: {automation.id} for {target_flow.name}"
                )
            except ValueError:
                automation = Automation(
                    name=target_flow.automation.name,
                    trigger=DeploymentEventTrigger(
                        expect={"prefect.flow-run.Completed"},
                        match_related={
                            "prefect.resource.name": target_flow.automation.automate_after_flow_name
                        },
                    ),
                    actions=[
                        RunDeployment(
                            deployment_id=deployment_id[0],
                            parameters={
                                "is_automated": True,
                                "previous_flow_run_id": "{{ flow_run.id }}",
                            },
                        )
                    ],
                ).create()
                print(f"Automation created: {automation.id} for {target_flow.name}")

        created_deployments_ids[target_flow.flow_object.name] = deployment_id[0]
        print(f"Pending deployments: {len(pending_deployments)}")
