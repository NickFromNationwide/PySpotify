import random
import secrets
import string

import bcrypt


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    return s


class AuthenticationLayer(object):
    def __init__(self):
        """
        Implements the auth layer in the spotify application.
        """
        self.chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        self.log_rounds = 13
        self.token_bytes = 62
        self.encode_type = 'utf-8'

    def generateSessionStateId(self, size=16):
        """Generates a 16 character Spotify state token always starting with S."""
        size = size - 1
        state_id = ''.join(random.choice(self.chars) for _ in range(size))
        state_id = "S" + state_id
        return state_id

    def generateUserMusicKeyId(self, size=16):
        """Generates a 16 character music_key_id always starting with M."""
        size = size - 2
        key_id = ''.join(random.choice(self.chars) for _ in range(size))
        key_id = 'M' + key_id + "0"
        return key_id

    def generateUserId(self, size=16):
        """Generates a 16 character user_id always starting with U."""
        size = size - 2
        user_id = ''.join(random.choice(self.chars) for _ in range(size))
        user_id = 'U' + user_id + "0"
        return user_id

    def generateLoginToken(self):
        """Generates an 85 character login token always starting with T."""
        token = secrets.token_urlsafe(self.token_bytes)
        token = "T" + token + "0"
        return token

    def hashPassword(self, plaintext_password, encode_plaintext_password=True):
        """Hashes a plaintext password and return the result."""
        if encode_plaintext_password:
            plaintext_password = plaintext_password.encode(self.encode_type)
        password_hash = bcrypt.hashpw(plaintext_password, bcrypt.gensalt(rounds=self.log_rounds))
        return password_hash

    def comparePasswordToHash(self, plaintext_password, hash_password, encode_plaintext_password=True):
        """Compares a plaintext password to a hash and return the Result."""
        if encode_plaintext_password:
            plaintext_password = plaintext_password.encode(self.encode_type)
        if bcrypt.hashpw(plaintext_password, hash_password) == hash_password:
            return True
        else:
            return False
