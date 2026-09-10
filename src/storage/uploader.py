"""
Free & Scalable Asset Hosting (Layer D).
Supports 100% Free Hosting Options:
1. Cloudflare R2 (10GB Free Storage, $0 Egress fees)
2. Local Cloudflare Tunnel / Ngrok (Public HTTPS tunnel to localhost for $0)
3. GitHub Raw / Pages CDN (100% Free public file hosting)
4. Local Static Web Server (Default for development and dry-run)
"""

import logging
import os
import requests
from pathlib import Path
from src.config import settings

logger = logging.getLogger(__name__)

class AssetUploader:
    def __init__(self):
        self.s3_endpoint = settings.s3_endpoint
        self.s3_bucket = settings.s3_bucket
        self.s3_access_key = settings.s3_access_key
        self.s3_secret_key = settings.s3_secret_key
        self.public_cdn_base = settings.public_cdn_base.rstrip("/")

    def upload_slide_images(self, image_paths: list[str], publication_date: str) -> list[str]:
        """
        Uploads or stages images and returns public URLs.
        Defaults to PUBLIC_CDN_BASE (e.g. your free tunnel, R2, or local server).
        """
        public_urls = []

        # 1. Cloudflare R2 (100% Free 10GB tier) or AWS S3
        if self.s3_bucket and self.s3_access_key and self.s3_secret_key:
            try:
                import boto3
                session = boto3.session.Session()
                s3 = session.client(
                    service_name='s3',
                    aws_access_key_id=self.s3_access_key,
                    aws_secret_access_key=self.s3_secret_key,
                    endpoint_url=self.s3_endpoint
                )
                for path_str in image_paths:
                    p = Path(path_str)
                    key = f"instagram/{publication_date}/{p.name}"
                    s3.upload_file(
                        str(p),
                        self.s3_bucket,
                        key,
                        ExtraArgs={'ContentType': 'image/jpeg'}
                    )
                    url = f"{self.public_cdn_base}/{key}"
                    public_urls.append(url)
                    logger.info(f"Uploaded {p.name} to free Cloudflare R2: {url}")
                return public_urls
            except ImportError:
                logger.warning("boto3 not installed, using CDN base URL formatting.")
            except Exception as e:
                logger.error(f"S3/R2 upload failed: {e}. Falling back to CDN base URL formatting.")

        # 2. Check if running in cloud (GitHub Actions / Render / Docker) or localhost without active tunnel
        use_cloud_upload = (
            "localhost" in self.public_cdn_base
            or "127.0.0.1" in self.public_cdn_base
            or os.environ.get("GITHUB_ACTIONS") == "true"
            or not self.public_cdn_base
        )

        if use_cloud_upload:
            logger.info("Using 100% Free Public Cloud CDN for Meta Instagram ingestion...")
            try:
                for path_str in image_paths:
                    p = Path(path_str)
                    with open(p, "rb") as f:
                        resp = requests.post(
                            "https://catbox.moe/user/api.php",
                            data={"reqtype": "fileupload"},
                            files={"fileToUpload": (p.name, f, "image/jpeg")},
                            timeout=25
                        )
                    if resp.status_code == 200 and resp.text.startswith("http"):
                        url = resp.text.strip()
                        public_urls.append(url)
                        logger.info(f"Uploaded {p.name} to free cloud CDN: {url}")
                    else:
                        raise RuntimeError(f"Cloud CDN upload returned: {resp.text}")
                return public_urls
            except Exception as e:
                logger.warning(f"Free cloud CDN upload error ({e}). Falling back to CDN base URL formatting.")
                public_urls = []

        # 3. Free Tunnel / Static Server URL staging (Ngrok / Cloudflare Tunnel)
        for path_str in image_paths:
            p = Path(path_str)
            relative_part = f"output/{p.parent.name}/{p.name}"
            public_url = f"{self.public_cdn_base}/{relative_part}"
            public_urls.append(public_url)

        return public_urls

uploader = AssetUploader()
