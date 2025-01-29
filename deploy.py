from prefect import deploy

from flows.test_flow import test_flow

REGISTERED_FLOWS = {
    "test_flow": test_flow.test_flow
}

if __name__ == "__main__":
    deployments = [REGISTERED_FLOWS[flow_name].to_deployment(flow_name) for flow_name in REGISTERED_FLOWS]

    deploy(
        *deployments,
        work_pool_name="test-docker",
        image="prefect_test:dev"
    )