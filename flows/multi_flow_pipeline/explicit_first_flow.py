from prefect import flow

from flows.multi_flow_pipeline.first_flow import do_something
from flows.multi_flow_pipeline.second_flow import second_flow


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def first_flow_explicit():
    x = do_something()
    second_flow(wait_for=[x])
