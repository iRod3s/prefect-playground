from prefect import deploy

from flows.example_flow import example

REGISTERED_FLOWS = {
    "test_flow": example.example_flow
}

if __name__ == "__main__":
    deployments = [REGISTERED_FLOWS[flow_name].to_deployment(flow_name) for flow_name in REGISTERED_FLOWS]

    deploy(
        *deployments,
        work_pool_name="test-docker",
        image="prefect_test:dev", 
        push=False
    )