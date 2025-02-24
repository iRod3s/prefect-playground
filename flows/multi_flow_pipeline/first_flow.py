from prefect import flow, task


@task()
def do_something() -> str:
    return "something"


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def first_flow():
    do_something()
