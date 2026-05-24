import aioboto3

from core.config.settings import get_settings

settings = get_settings()


class S3StorageClient:
    def __init__(self) -> None:
        self.bucket = settings.aws_s3_bucket_name
        self.region = settings.aws_region

        # Build explicit credentials only when both keys are present.
        # When running on EC2 / ECS with an IAM role, leave them out so
        # boto3 falls back to the instance-metadata credential chain.
        session_kwargs: dict = {"region_name": self.region}
        if settings.aws_access_key_id is not None and settings.aws_secret_access_key is not None:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id.get_secret_value()
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key.get_secret_value()

        self._session = aioboto3.Session(**session_kwargs)

        # None → real AWS S3 (prod / IAM role)
        # set  → MinIO or any S3-compatible endpoint (local/Docker)
        self._endpoint_url = settings.aws_endpoint_url or None

    async def upload_file(
        self,
        file_bytes: bytes,
        key: str,
        content_type: str,
    ) -> str:
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )

        # MinIO local URL vs real S3 URL
        if self._endpoint_url:
            return f"{self._endpoint_url}/{self.bucket}/{key}"

        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    async def delete_file(self, key: str) -> None:
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
        ) as s3:
            await s3.delete_object(
                Bucket=self.bucket,
                Key=key,
            )
