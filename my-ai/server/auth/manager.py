import time
import secrets
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, auth_token: str = ""):
        self.auth_token = auth_token
        self.active_sessions = {}
        self.device_tokens = {}

    def validate_token(self, token: str) -> bool:
        if not self.auth_token:
            return True
        return secrets.compare_digest(token, self.auth_token)

    def create_session(self, device_id: str = "") -> str:
        session_token = secrets.token_hex(32)
        self.active_sessions[session_token] = {
            "device_id": device_id,
            "created_at": time.time(),
            "last_activity": time.time()
        }
        return session_token

    def validate_session(self, session_token: str) -> bool:
        if session_token not in self.active_sessions:
            return False
        session = self.active_sessions[session_token]
        session["last_activity"] = time.time()
        if time.time() - session["created_at"] > 86400:
            del self.active_sessions[session_token]
            return False
        return True

    def register_device(self, device_name: str, device_type: str = "android") -> str:
        device_token = secrets.token_hex(16)
        self.device_tokens[device_token] = {
            "name": device_name,
            "type": device_type,
            "registered_at": time.time(),
            "capabilities": []
        }
        return device_token

    def validate_device(self, device_token: str) -> Optional[dict]:
        return self.device_tokens.get(device_token)

    def get_active_devices(self) -> list[dict]:
        return [
            {"token": k, **v}
            for k, v in self.device_tokens.items()
        ]
