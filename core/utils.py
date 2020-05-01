import bcrypt  # type: ignore
import base64
from typing import Optional
from cryptography.fernet import Fernet
import motor.motor_asyncio as aiomotor
from core.db import get_secret_id
from settings import crypt_key


async def validate_secret_key(mongo: aiomotor.AsyncIOMotorDatabase, secret_key: str) -> Optional[str]:
    """Gets and validates secret_key

    :param mongo: Connection to the database
    :type mongo: AsyncIOMotorDatabase
    :param secret_key: Secret key to be checked if it exists in DB
    :type secret_key: str
    :return: Error message if secret key doesnt exist
        (default is None)
    :rtype: Optional[str]
    """

    error = None
    secret = await get_secret_id(mongo.secret, secret_key)
    if not secret:
        error = 'wrong secret key'
    return error


def generate_phrase_hash(phrase: str, salt_rounds: int = 12) -> str:
    """Gets and hashes code phrase

    :param phrase: Code phrase to be hashed
    :type phrase: str
    :param salt_rounds: Number of rounds for hashing a phrase
        (default is 12)
    :type salt_rounds: int
    :return: Hashed code phrased
    :rtype: str
    """

    secret_bin = phrase.encode('utf-8')
    hashed = bcrypt.hashpw(secret_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


def check_phrase_hash(encoded: str, phrase: str) -> bool:
    """Gets code phrase and compares it with hashed phrase in database

    :param encoded: Hashed phrase from database
    :type encoded: str
    :param phrase: Phrase to be compared
    :type phrase: str
    :return: True if code phrase is correct
    :rtype: bool
    """
    phrase_bytes = phrase.encode('utf-8')
    encoded_bytes = encoded.encode('utf-8')

    hashed = base64.b64decode(encoded_bytes)
    is_correct = bcrypt.hashpw(phrase_bytes, hashed) == hashed
    return is_correct


def encrypt_secret(secret: str) -> bytes:
    """Gets and encrypts secret

    :param secret: Secret to be encrypted
    :type secret: str
    :return: Encrypted string of bytes
    :rtype: bytes
    """
    f = Fernet(crypt_key)
    encoded = secret.encode('utf-8')
    encrypted = f.encrypt(encoded)
    return encrypted


def decrypt_secret(encrypted_secret: bytes) -> str:
    """Gets and decrypts secret

    :param encrypted_secret: String of bytes to be decrypted
    :type encrypted_secret: bytes
    :return: Decrypted string
    :rtype: str
    """
    f = Fernet(crypt_key)
    decrypted = f.decrypt(encrypted_secret)
    secret = decrypted.decode('utf-8')
    return secret
