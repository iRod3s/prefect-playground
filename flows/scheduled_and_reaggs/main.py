from prefect import flow, task
from prefect.context import get_run_context, FlowRunContext

import pendulum
from pendulum import Date
import random


@task(task_run_name="simulate_generating_time_series_data_for_{date}")
def simulate_generating_time_series_data(date: Date) -> dict[str, str]:
    return {
        "date": date.to_date_string(),
        "values": random.randint(0, 100),
    }


@task()
def report_scheduling(start_date: Date, end_date: Date, step: str = "days") -> None:
    execution_interval = pendulum.interval(start_date, end_date)

    print(
        f"Processing data from {start_date.to_date_string()} to {end_date.to_date_string()} with step {step}"
    )
    print(
        f"Processed dates: {[x.to_date_string() for x in execution_interval.range(step)]}"
    )

    return None


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def scheduled_flow(start_date: str | None = None, end_date: str | None = None):
    context: FlowRunContext = get_run_context()

    if context.flow_run.auto_scheduled:
        processing_start_date = context.flow_run.expected_start_time
        processing_end_date = context.flow_run.next_scheduled_start_time
    else:
        processing_start_date = pendulum.parse(start_date)
        processing_end_date = pendulum.parse(end_date)

    scheduling_report = report_scheduling(
        start_date=processing_start_date, end_date=processing_end_date
    )

    execution_interval = pendulum.interval(processing_start_date, processing_end_date)

    results = []

    for date in execution_interval.range("days"):
        data = simulate_generating_time_series_data(date, wait_for=[scheduling_report])
        results.append(data)
