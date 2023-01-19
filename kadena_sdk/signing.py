from nacl.signing import SigningKey
import base64
import hashlib

def hash_and_sign(s, priv_key):
  # Turn the json into a byte string
  cmd_data = bytes(s, encoding="utf8")

  # Create the signature
  sk = SigningKey(bytes.fromhex(priv_key))

  # Create the hash code
  hash_bytes = blake2b(cmd_data)
  hash_code = base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')
  
  return hash_code, sk.sign(hash_bytes).signature.hex()


def blake2b(bytes):
  hash2b = hashlib.blake2b(bytes, digest_size=32)
  return hash2b.digest()