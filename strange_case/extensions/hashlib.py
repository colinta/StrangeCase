from __future__ import absolute_import
import hashlib


def sha(s):
    bytes = s.encode('utf-8')
    return hashlib.sha1(bytes).hexdigest()
md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()
