"""
storage.py - Stockage MinIO/S3

Description:
Helpers pour upload documents sur MinIO et gestion bucket.
"""

from io import BytesIO
from minio import Minio
from minio.error import S3Error
from app.config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket_exists(bucket_name: str) -> None:
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def upload_bytes(
    bucket_name: str,
    object_name: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    client = get_minio_client()
    ensure_bucket_exists(bucket_name)

    data = BytesIO(content)
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data,
        length=len(content),
        content_type=content_type,
    )

    scheme = "https" if settings.MINIO_SECURE else "http"
    return f"{scheme}://{settings.MINIO_ENDPOINT}/{bucket_name}/{object_name}"
