from prefect import flow, task

import random

@task
def generate_number(min: int, max: int) -> int:
    return random.randint(min, max)


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def example_flow(min: int = 0, max: int = 100):
    number = generate_number(min, max)
    print(f"{number} has been generated!")

    return number

