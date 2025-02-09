from prefect.testing.utilities import prefect_test_harness
from flows.example_flow.example import example_flow, generate_number


def test_task1():
    result = generate_number.fn(min=1, max=100)
    assert 1 <= result <= 100


def test_test_flow():
    with prefect_test_harness():
        result = example_flow()
        assert 1 <= result <= 100
