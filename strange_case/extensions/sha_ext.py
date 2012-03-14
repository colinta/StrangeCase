import hashlib


def sha_filter(s):
    sha = hashlib.sha1()
    sha.update(s)
    return sha.hexdigest()
