"""
Authentication & Security utilities
Zero plaintext passwords — bcrypt only
"""
import bcrypt
import os
from datetime import datetime, timedelta

class PasswordManager:
    """
    Bcrypt password hashing manager
    """
    
    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Hash a plaintext password with bcrypt
        
        Args:
            plaintext: Raw password string
        
        Returns:
            Bcrypt hash string (safe to store in DB)
        """
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good security
        hashed = bcrypt.hashpw(plaintext.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plaintext: str, hashed: str) -> bool:
        """
        Verify a plaintext password against stored hash
        
        Args:
            plaintext: Raw password to verify
            hashed: Stored bcrypt hash
        
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(
                plaintext.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False

# ===== ENVIRONMENT VARIABLE VALIDATOR =====

REQUIRED_ENV_VARS = [
    'DATABASE_URL',
    'MQTT_BROKER',
    'MQTT_USERNAME',
    'MQTT_PASSWORD'
]

def validate_environment():
    """
    Ensure all required environment variables are set
    No plaintext secrets in code
    
    Raises:
        EnvironmentError if any required variable is missing
    """
    missing = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {missing}\n"
            f"Set them in .env file or docker-compose.yml"
        )
    
    print("✅ Environment variables validated")

# ===== HARDCODED SECRET SCANNER =====

FORBIDDEN_PATTERNS = [
    'password123',
    'admin123',
    'secret',
    'twinpac123'  # Default password must be changed in production
]

def warn_default_credentials():
    """
    Warn if default credentials are still in use
    """
    mqtt_pass = os.getenv('MQTT_PASSWORD', '')
    db_url = os.getenv('DATABASE_URL', '')
    
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in mqtt_pass or pattern in db_url:
            print(f"⚠️  WARNING: Default credential detected ({pattern})")
            print("   Change all passwords before production deployment!")
