"""Data models for URL Shortener."""
import random
import string
import io
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Optional


ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 6) -> str:
    return "".join(random.choices(ALPHABET, k=length))


def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def make_qr_base64(url: str, box_size: int = 6) -> str:
    """Return a base64-encoded PNG QR code for the given URL."""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#7c6af7", back_color="#0f0f1a")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        return ""


@dataclass
class ShortURL:
    code: str
    long_url: str
    alias: Optional[str]
    clicks: int
    created_at: str
    last_click: Optional[str]
    expires_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "ShortURL":
        return cls(
            code=row["code"],
            long_url=row["long_url"],
            alias=row["alias"],
            clicks=row["clicks"],
            created_at=row["created_at"],
            last_click=row["last_click"],
            expires_at=row["expires_at"] if "expires_at" in row.keys() else None,
        )

    @property
    def display_code(self) -> str:
        return self.alias or self.code

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        try:
            exp = datetime.fromisoformat(self.expires_at)
            return datetime.now() > exp
        except Exception:
            return False

    def short_link(self, base: str = "http://localhost:5000") -> str:
        return f"{base}/{self.display_code}"

    def preview_link(self, base: str = "http://localhost:5000") -> str:
        return f"{base}/+{self.display_code}"
