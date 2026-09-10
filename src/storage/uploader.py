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
        
        base = (settings.public_cdn_base or "").strip().rstrip("/")
        if not base or "localhost" in base or "127.0.0.1" in base:
            base = os.environ.get("RENDER_EXTERNAL_URL", "https://autogram-dashboard.onrender.com").rstrip("/")
        self.public_cdn_base = base

    def _upload_to_freeimage(self, p: Path) -> str:
        """Uploads image to freeimage.host returning a direct Cloudflare CDN URL."""
        resp = requests.post(
            "https://freeimage.host/api/1/upload",
            data={"key": "6d207e02198a847aa98d0a2a901485a5", "action": "upload", "format": "json"},
            files={"source": (p.name, open(p, "rb"), "image/jpeg")},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            url = data.get("image", {}).get("url", "")
            if url.startswith("http"):
                return url
        raise RuntimeError(f"freeimage.host returned status {resp.status_code}: {resp.text[:200]}")

    def _upload_to_catbox(self, p: Path) -> str:
        """Uploads image to catbox.moe returning a direct CDN URL."""
        with open(p, "rb") as f:
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (p.name, f, "image/jpeg")},
                timeout=25
            )
        if resp.status_code == 200 and resp.text.strip().startswith("http"):
            return resp.text.strip()
        raise RuntimeError(f"catbox returned status {resp.status_code}: {resp.text[:200]}")

    def upload_slide_images(self, image_paths: list[str], publication_date: str, dry_run: bool | None = None) -> list[str]:
        """
        Uploads or stages images and returns public URLs.
        Cascade:
        0. If dry_run is True, formats public staging URLs instantly without upload.
        1. S3 / Cloudflare R2 if configured.
        2. freeimage.host cloud CDN (works in GitHub Actions & datacenter IPs).
        3. catbox.moe cloud CDN fallback.
        4. Render Dashboard / PUBLIC_CDN_BASE fallback.
        Always guarantees valid absolute public HTTP/HTTPS URLs.
        """
        is_dry = dry_run if dry_run is not None else (settings.dry_run or os.environ.get("DRY_RUN") == "true")
        fallback_base = self.public_cdn_base if (self.public_cdn_base.startswith("http://") or self.public_cdn_base.startswith("https://")) else "https://autogram-dashboard.onrender.com"
        
        if is_dry:
            logger.info("[DRY-RUN] Staging image URLs with public base without external upload.")
            return [f"{fallback_base.rstrip('/')}/output/{Path(p).parent.name}/{Path(p).name}" for p in image_paths]

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
                    logger.info(f"Uploaded {p.name} to Cloudflare R2: {url}")
                return public_urls
            except ImportError:
                logger.warning("boto3 not installed, falling back to cloud image hosts.")
            except Exception as e:
                logger.error(f"S3/R2 upload failed: {e}. Falling back to cloud image hosts.")

        # 2. Check if running in cloud, GitHub Actions, or local without S3
        use_cloud_upload = (
            "localhost" in self.public_cdn_base
            or "127.0.0.1" in self.public_cdn_base
            or "ngrok" in self.public_cdn_base
            or os.environ.get("GITHUB_ACTIONS") == "true"
            or not (self.s3_bucket and self.s3_access_key)
        )

        if use_cloud_upload:
            logger.info("Using 100% Free Public Cloud CDN for Meta Instagram ingestion...")
            all_uploaded = True
            temp_urls = []

            for path_str in image_paths:
                p = Path(path_str)
                uploaded_url = None

                # Primary: freeimage.host
                try:
                    uploaded_url = self._upload_to_freeimage(p)
                    logger.info(f"Uploaded {p.name} to freeimage.host: {uploaded_url}")
                except Exception as e1:
                    logger.warning(f"freeimage.host failed for {p.name}: {e1}. Trying catbox...")
                    # Secondary: catbox.moe
                    try:
                        uploaded_url = self._upload_to_catbox(p)
                        logger.info(f"Uploaded {p.name} to catbox.moe: {uploaded_url}")
                    except Exception as e2:
                        logger.warning(f"catbox.moe also failed for {p.name}: {e2}")

                if uploaded_url:
                    temp_urls.append(uploaded_url)
                else:
                    all_uploaded = False
                    break

            if all_uploaded and len(temp_urls) == len(image_paths):
                return temp_urls
            else:
                logger.warning("Cloud image host cascade incomplete. Falling back to PUBLIC_CDN_BASE...")

        # 3. Fallback to PUBLIC_CDN_BASE (e.g. Render dashboard or tunnel)
        fallback_base = self.public_cdn_base if (self.public_cdn_base.startswith("http://") or self.public_cdn_base.startswith("https://")) else "https://autogram-dashboard.onrender.com"
        for path_str in image_paths:
            p = Path(path_str)
            relative_part = f"output/{p.parent.name}/{p.name}"
            public_url = f"{fallback_base.rstrip('/')}/{relative_part}"
            public_urls.append(public_url)

        return public_urls

uploader = AssetUploader()
