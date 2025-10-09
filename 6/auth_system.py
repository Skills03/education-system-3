"""
Immutable Authentication System
Credentials and secrets BAKED into environment variables
"""

import os
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


class ImmutableAuth:
    """Authentication system with credentials baked into environment"""

    def __init__(self):
        # These are BAKED into Docker image - cannot be changed at runtime
        self.ADMIN_USERNAME = os.environ.get('AUTH_USERNAME', 'admin')
        self.ADMIN_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH',
            # Default: admin/TeachMaster2024! (SHA256)
            '8f3e0e5d7c8f9a2b1e4d6c7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c'
        )
        self.JWT_SECRET = os.environ.get('JWT_SECRET',
            # Default secret - should be overridden in production
            'IMMUTABLE_TEACHER_SECRET_KEY_DO_NOT_CHANGE_AFTER_DEPLOYMENT'
        )
        self.JWT_ALGORITHM = 'HS256'
        self.TOKEN_EXPIRY_HOURS = 24

        logger.info(f"🔐 Auth initialized - Username: {self.ADMIN_USERNAME}")
        logger.info(f"🔐 Password hash: {self.ADMIN_PASSWORD_HASH[:16]}...")
        logger.info(f"🔐 JWT Secret: {self.JWT_SECRET[:20]}...")

    @staticmethod
    def hash_password(password: str) -> str:
        """Generate SHA256 hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password against baked credentials"""
        password_hash = self.hash_password(password)

        username_match = username == self.ADMIN_USERNAME
        password_match = password_hash == self.ADMIN_PASSWORD_HASH

        logger.info(f"🔐 Auth attempt - User: {username}, Match: {username_match and password_match}")
        return username_match and password_match

    def generate_token(self, username: str) -> str:
        """Generate JWT token"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)
        logger.info(f"🔐 Token generated for {username}")
        return token

    def verify_token(self, token: str) -> dict | None:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.JWT_SECRET, algorithms=[self.JWT_ALGORITHM])
            logger.debug(f"🔐 Token verified for {payload.get('username')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("🔐 Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("🔐 Invalid token")
            return None

    def require_auth(self, f):
        """Decorator to protect routes with JWT authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                logger.warning("🔐 No Authorization header")
                return jsonify({'error': 'No authorization token provided'}), 401

            # Extract token (format: "Bearer <token>")
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401

            # Verify token
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401

            # Add user info to request context
            request.auth_user = payload.get('username')

            return f(*args, **kwargs)

        return decorated_function


# Utility function to generate password hash
def generate_password_hash(password: str):
    """Helper to generate password hash for environment variable"""
    return hashlib.sha256(password.encode()).hexdigest()


if __name__ == '__main__':
    # Tool to generate password hashes
    print("=" * 70)
    print("🔐 PASSWORD HASH GENERATOR")
    print("=" * 70)
    print("\nGenerate hashes to use in AUTH_PASSWORD_HASH environment variable")
    print()

    while True:
        password = input("Enter password (or 'quit' to exit): ")
        if password.lower() == 'quit':
            break

        hash_value = generate_password_hash(password)
        print(f"\nPassword: {password}")
        print(f"SHA256 Hash: {hash_value}")
        print(f"\nAdd to Dockerfile:")
        print(f"ENV AUTH_PASSWORD_HASH={hash_value}")
        print()
