from __future__ import annotations

import base64
from pathlib import Path

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.exceptions import BadSignatureError
except Exception as exc:  # pragma: no cover
    SigningKey = None
    VerifyKey = None
    BadSignatureError = Exception
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class CryptoUnavailable(RuntimeError):
    pass


def _ensure_crypto() -> None:
    if SigningKey is None or VerifyKey is None:
        raise CryptoUnavailable(
            "PyNaCl is required. Install dependencies with: pip install -r requirements.txt"
        ) from _IMPORT_ERROR


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def generate_keypair() -> tuple[bytes, bytes]:
    _ensure_crypto()
    sk = SigningKey.generate()
    vk = sk.verify_key
    return bytes(sk), bytes(vk)


def save_keypair(private_key: bytes, public_key: bytes, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "publisher_private.pem").write_text(
        "AZSOS ED25519 PRIVATE KEY\n" + b64e(private_key) + "\n", encoding="utf-8"
    )
    (out_dir / "publisher_public.pem").write_text(
        "AZSOS ED25519 PUBLIC KEY\n" + b64e(public_key) + "\n", encoding="utf-8"
    )


def load_private_key(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").strip().splitlines()
    payload = text[-1].strip()
    return b64d(payload)


def load_public_key(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8").strip().splitlines()
    payload = text[-1].strip()
    return b64d(payload)


def sign(private_key: bytes, payload: bytes) -> bytes:
    _ensure_crypto()
    return SigningKey(private_key).sign(payload).signature


def verify(public_key: bytes, payload: bytes, signature: bytes) -> bool:
    _ensure_crypto()
    try:
        VerifyKey(public_key).verify(payload, signature)
        return True
    except BadSignatureError:
        return False


def fingerprint(public_key: bytes) -> str:
    import hashlib

    digest = hashlib.sha256(public_key).hexdigest().upper()
    return " ".join(digest[i : i + 4] for i in range(0, 32, 4))


def public_from_private(private_key: bytes) -> bytes:
    _ensure_crypto()
    return bytes(SigningKey(private_key).verify_key)
