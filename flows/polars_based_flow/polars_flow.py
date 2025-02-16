from prefect import flow, task
import polars as pl

import random


@task
def generate_df(number_of_rows: int = 1000) -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "a": pl.Series(
                "a", [random.randint(0, 100) for _ in range(number_of_rows)]
            ),
            "b": pl.Series(
                "b", [random.randint(0, 100) for _ in range(number_of_rows)]
            ),
        }
    )

    print(df)
    return df


def calculate_values(df: pl.DataFrame) -> tuple[int, int, int]:
    min = df.select("a").min().item()
    max = df.select("a").max().item()
    mean = df.select("a").mean().item()

    return min, max, mean


@flow(retries=3, retry_delay_seconds=5, log_prints=True)
def polars_flow(min: int = 0, max: int = 100):
    data = generate_df()

    min, max, mean = calculate_values(data)
    return min, max, mean
