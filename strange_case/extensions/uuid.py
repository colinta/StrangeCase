"""
Usage::

    <id>{{ 'http://myhost.com/articles'|uuid('url') }}</id>
"""
from __future__ import absolute_import
from uuid import uuid5
from uuid import NAMESPACE_DNS
from uuid import NAMESPACE_URL
from uuid import NAMESPACE_OID
from uuid import NAMESPACE_X500


_namespaces = {
        'dns': NAMESPACE_DNS,
        'url': NAMESPACE_URL,
        'oid': NAMESPACE_OID,
        'X500': NAMESPACE_X500,
        }


def uuid(value, namespace='url'):
    return str(uuid5(_namespaces[namespace], value))


def urn(value, namespace='url'):
    return str(uuid5(_namespaces[namespace], value).urn)
