from prefect import flow, task

import random

def deploy():
    test_flow.deploy(
       name="test_flow",
       work_pool_name="default",
       image=None
    )

@task
def generate_number(min: int, max: int) -> int:
    return random.randint(min, max)


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def test_flow(min: int = 0, max: int = 100):
    number = generate_number(min, max)
    print(f"{number} has been generated!")


if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/username/repository.git",
        entrypoint="path/to/your/flow.py:your_flow_function"
    ).deploy(
        name="my-deployment",
        work_pool_name="my-work-pool",
    )