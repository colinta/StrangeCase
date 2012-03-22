import hashlib


def sha(s):
    sha = hashlib.sha1()
    sha.update(s)
    return sha.hexdigest()
