import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import auth_utils

try:
    print("Testing hash...")
    # Try encoding to bytes
    # h = auth_utils.get_password_hash("password".encode('utf-8')) 
    # Wait, passlib might complain if it's bytes.
    # Let's try to see if we can use bcrypt directly to confirm it works.
    import bcrypt
    print(f"Bcrypt version: {bcrypt.__version__}")
    
    # This is what passlib likely does internally
    # bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())
    
    h = auth_utils.get_password_hash("password")
    print(f"Hash result: {h}")
except Exception as e:
    print(f"Error: {e}")
