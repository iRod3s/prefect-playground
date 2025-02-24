from prefect import flow, task


@task()
def do_another_something() -> str:
    return "another something"


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def second_flow(
    is_automated: bool = False, previous_flow_run_id: str | None = None
) -> None:
    if is_automated:
        print(f"Triggered by flow run: {previous_flow_run_id}")
    do_another_something()
