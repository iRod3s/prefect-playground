from prefect_aws import AwsCredentials, S3Bucket, AwsClientParameters


def register_blocks() -> None:
    credentials = AwsCredentials(
        aws_access_key_id="miniouser",
        aws_secret_access_key="miniopassword",
        aws_client_parameters=AwsClientParameters(
            endpoint_url="http://localhost:9000",
        ),
    )

    credentials.save(name="default-aws-credentials", overwrite=False)

    prefect_results_storage_bucket = S3Bucket(
        credentials=credentials,
        bucket_name="prefect-results-storage",
    )

    prefect_results_storage_bucket.save(
        name="prefect-results-storage-bucket", overwrite=False
    )


if __name__ == "__main__":
    register_blocks()
