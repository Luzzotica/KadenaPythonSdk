from nacl.signing import SigningKey
import base64
import hashlib
import json

def hash_and_sign(s, priv_key):
  # Turn the json into a byte string
  cmd_data = bytes(s, encoding="utf8")

  # Create the signature
  sk = SigningKey(bytes.fromhex(priv_key))

  # Create the hash code
  hash_bytes = blake2b(cmd_data)
  hash_code = base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')
  
  return hash_code, sk.sign(hash_bytes).signature.hex()


def sign(hash, priv_key):
  """Accepts a blake hash and a private key and returns a signature."""
  sk = SigningKey(bytes.fromhex(priv_key))

  # Get the bytes from the hash
  hash_bytes = base64.urlsafe_b64decode(f'{hash}==')

  return sk.sign(hash_bytes).signature.hex()


def blake_hash(value):
  """Blake2b hashes a string or dict."""
  
  if type(value) is str:
    hash_bytes = blake2b(bytes(value, encoding="utf8"))
    return base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')
  elif type(value) is dict:
    s = json.dumps(value, separators=(',', ':'))
    hash_bytes = blake2b(bytes(s, encoding="utf8"))
    return base64.urlsafe_b64encode(hash_bytes).decode().rstrip('=')

  raise Exception(f'Invalid type: {type(value)}')

def blake2b(bytes, digest_size=32):
  hash2b = hashlib.blake2b(bytes, digest_size=digest_size)
  return hash2b.digest()


