from __future__ import absolute_import
import hashlib


sha = lambda s: hashlib.sha1(s).hexdigest()
md5 = lambda s: hashlib.md5(s).hexdigest()
