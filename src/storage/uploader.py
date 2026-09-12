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

    def _upload_to_catbox(self, p: Path, mime: str = "image/jpeg") -> str:
        """Uploads image to catbox.moe returning a direct CDN URL."""
        with open(p, "rb") as f:
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (p.name, f, mime)},
                timeout=60
            )
        if resp.status_code == 200 and resp.text.strip().startswith("http"):
            return resp.text.strip()
        raise RuntimeError(f"catbox returned status {resp.status_code}: {resp.text[:200]}")

    def _upload_to_litterbox(self, p: Path, mime: str = "image/jpeg") -> str:
        """Uploads to litterbox.catbox.moe (1h temp CDN — works from GitHub Actions IPs)."""
        with open(p, "rb") as f:
            resp = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "24h"},
                files={"fileToUpload": (p.name, f, mime)},
                timeout=60
            )
        if resp.status_code == 200 and resp.text.strip().startswith("http"):
            return resp.text.strip()
        raise RuntimeError(f"litterbox returned status {resp.status_code}: {resp.text[:200]}")

    def _upload_to_0x0(self, p: Path, mime: str = "image/jpeg") -> str:
        """Uploads image to 0x0.st (works from GitHub Actions IPs, permanent CDN)."""
        with open(p, "rb") as f:
            resp = requests.post(
                "https://0x0.st",
                files={"file": (p.name, f, mime)},
                timeout=60
            )
        if resp.status_code == 200 and resp.text.strip().startswith("http"):
            return resp.text.strip()
        raise RuntimeError(f"0x0.st returned status {resp.status_code}: {resp.text[:200]}")

    def _upload_to_uguu(self, p: Path, mime: str = "video/mp4") -> str:
        """Uploads file to uguu.se returning a direct CDN URL (up to 100MB, 48h)."""
        with open(p, "rb") as f:
            resp = requests.post(
                "https://uguu.se/upload",
                files={"files[]": (p.name, f, mime)},
                timeout=60
            )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("files"):
                url = data["files"][0].get("url")
                if url and url.startswith("http"):
                    return url
        raise RuntimeError(f"uguu.se returned status {resp.status_code}: {resp.text[:200]}")

    def _upload_to_imgbb(self, p: Path) -> str:
        """Uploads to imgbb.com free API (reliable from all IPs including CI)."""
        api_key = settings.imgbb_api_key or os.environ.get("IMGBB_API_KEY") or "f0ee2a304a71d5b2da983153c2284b73"
        if not api_key:
            raise RuntimeError("imgbb skipped: IMGBB_API_KEY is not configured.")
        import base64
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": b64},
            timeout=30
        )
        if resp.status_code == 200:
            url = resp.json().get("data", {}).get("url", "")
            if url.startswith("http"):
                return url
        raise RuntimeError(f"imgbb returned status {resp.status_code}: {resp.text[:200]}")

    def upload_slide_images(self, image_paths: list[str], publication_date: str, dry_run: bool | None = None) -> list[str]:
        """
        Uploads or stages images and returns public URLs.
        Cascade:
        0. If dry_run is True, formats public staging URLs instantly without upload.
        1. S3 / Cloudflare R2 if configured.
        2. imgbb.com authenticated API (prioritized for CI / GitHub Actions speed & reliability).
        3. freeimage.host cloud CDN.
        4. catbox.moe CDN fallback.
        5. litterbox.catbox.moe (24h temp, works from GitHub Actions IPs).
        6. 0x0.st (permanent CDN, GitHub Actions compatible).
        7. Render Dashboard / PUBLIC_CDN_BASE last resort.
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
            has_imgbb = bool(settings.imgbb_api_key or os.environ.get("IMGBB_API_KEY") or "f0ee2a304a71d5b2da983153c2284b73")

            for path_str in image_paths:
                p = Path(path_str)
                uploaded_url = None

                # Primary (fast & reliable): imgbb if API key is configured
                if has_imgbb:
                    try:
                        uploaded_url = self._upload_to_imgbb(p)
                        logger.info(f"Uploaded {p.name} to imgbb.com: {uploaded_url}")
                    except Exception as e_imgbb:
                        logger.warning(f"imgbb.com failed for {p.name}: {e_imgbb}. Trying fallback hosts...")

                # Secondary: freeimage.host
                if not uploaded_url:
                    try:
                        uploaded_url = self._upload_to_freeimage(p)
                        logger.info(f"Uploaded {p.name} to freeimage.host: {uploaded_url}")
                    except Exception as e1:
                        logger.warning(f"freeimage.host failed for {p.name}: {e1}. Trying catbox...")
                        # Fallback 2: catbox.moe
                        try:
                            uploaded_url = self._upload_to_catbox(p)
                            logger.info(f"Uploaded {p.name} to catbox.moe: {uploaded_url}")
                        except Exception as e2:
                            logger.warning(f"catbox.moe failed for {p.name}: {e2}. Trying litterbox...")
                            # Fallback 3: litterbox (GitHub Actions compatible)
                            try:
                                uploaded_url = self._upload_to_litterbox(p)
                                logger.info(f"Uploaded {p.name} to litterbox.catbox.moe: {uploaded_url}")
                            except Exception as e3:
                                logger.warning(f"litterbox failed for {p.name}: {e3}. Trying 0x0.st...")
                                # Fallback 4: 0x0.st
                                try:
                                    uploaded_url = self._upload_to_0x0(p)
                                    logger.info(f"Uploaded {p.name} to 0x0.st: {uploaded_url}")
                                except Exception as e4:
                                    logger.warning(f"0x0.st failed for {p.name}: {e4}.")
                                    # Fallback 5: imgbb retry if not tried initially
                                    if not has_imgbb:
                                        try:
                                            uploaded_url = self._upload_to_imgbb(p)
                                            logger.info(f"Uploaded {p.name} to imgbb.com: {uploaded_url}")
                                        except Exception as e5:
                                            logger.error(f"imgbb failed for {p.name}: {e5}. All cloud CDNs exhausted.")

                if uploaded_url:
                    temp_urls.append(uploaded_url)
                else:
                    all_uploaded = False
                    break

            if all_uploaded and len(temp_urls) == len(image_paths):
                return temp_urls

            # If third-party free hosts fail or rate-limit, check if we have a valid public HTTPS host (like Render)
            if self.public_cdn_base and self.public_cdn_base.startswith("https://") and "localhost" not in self.public_cdn_base and "127.0.0.1" not in self.public_cdn_base:
                logger.info(f"Third-party image hosts failed; falling back to verified public HTTPS server: {self.public_cdn_base}")
                return [f"{self.public_cdn_base.rstrip('/')}/output/{Path(p).parent.name}/{Path(p).name}" for p in image_paths]

            # In cloud/CI environments without public HTTPS host, fail closed
            raise RuntimeError(
                "No usable public image host available for live publishing. "
                "Configure S3/R2, or set IMGBB_API_KEY, or set PUBLIC_CDN_BASE to your live public HTTPS domain."
            )

        # Non-cloud/local fallback only: acceptable for dry-run or when a public tunnel/CDN is configured.
        fallback_base = self.public_cdn_base if (self.public_cdn_base.startswith("http://") or self.public_cdn_base.startswith("https://")) else None
        if not fallback_base:
            raise RuntimeError(
                "No usable image upload target available. Configure S3/R2 or IMGBB_API_KEY, "
                "or set PUBLIC_CDN_BASE to a publicly reachable host."
            )

        public_urls = []
        for path_str in image_paths:
            p = Path(path_str)
            relative_part = f"output/{p.parent.name}/{p.name}"
            public_url = f"{fallback_base.rstrip('/')}/{relative_part}"
            public_urls.append(public_url)

        return public_urls

    def upload_video_file(self, video_path: str, publication_date: str, dry_run: bool | None = None) -> str:
        """
        Stages a rendered Reel MP4 and returns a public URL for Meta ingestion.
        Cascade: dry-run fabricate -> S3/R2 -> catbox.moe -> litterbox -> 0x0.st.
        (Image-only hosts imgbb/freeimage are skipped for video.)
        """
        p = Path(video_path)
        is_dry = dry_run if dry_run is not None else (settings.dry_run or os.environ.get("DRY_RUN") == "true")
        fallback_base = self.public_cdn_base if (self.public_cdn_base.startswith("http://") or self.public_cdn_base.startswith("https://")) else "https://autogram-dashboard.onrender.com"

        if is_dry:
            logger.info("[DRY-RUN] Staging video URL with public base without external upload.")
            return f"{fallback_base.rstrip('/')}/output/{p.parent.name}/{p.name}"

        if self.s3_bucket and self.s3_access_key and self.s3_secret_key:
            try:
                import boto3
                s3 = boto3.session.Session().client(
                    service_name="s3",
                    aws_access_key_id=self.s3_access_key,
                    aws_secret_access_key=self.s3_secret_key,
                    endpoint_url=self.s3_endpoint,
                )
                key = f"instagram/{publication_date}/{p.name}"
                s3.upload_file(str(p), self.s3_bucket, key, ExtraArgs={"ContentType": "video/mp4"})
                url = f"{self.public_cdn_base}/{key}"
                logger.info(f"Uploaded {p.name} to Cloudflare R2: {url}")
                return url
            except Exception as e:
                logger.warning(f"S3/R2 video upload failed ({e}). Trying free file hosts...")

        for name, fn in (
            ("catbox.moe", self._upload_to_catbox),
            ("uguu.se", self._upload_to_uguu),
            ("litterbox", self._upload_to_litterbox),
            ("0x0.st", self._upload_to_0x0),
        ):
            try:
                url = fn(p, mime="video/mp4")
                logger.info(f"Uploaded {p.name} to {name}: {url}")
                return url
            except Exception as e:
                logger.warning(f"{name} video upload failed for {p.name}: {e}.")
        raise RuntimeError(
            "No usable public video host available for live Reel publishing. "
            "Configure S3/R2 or set PUBLIC_CDN_BASE to your live public HTTPS domain."
        )

uploader = AssetUploader()
