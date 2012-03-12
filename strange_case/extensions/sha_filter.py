import sha


def sha_filter(s):
    return sha.new(s).hexdigest()
