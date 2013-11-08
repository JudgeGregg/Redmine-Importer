#-*- encoding: utf8 -*-
"""Retrieve user id from ldap server."""
import logging
import sys

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

try:
    import ldap
except ImportError, exception:
    LOGGER.error(str(exception))
    sys.exit()

LDAP_SERVER_URL = 'ldap://directory.lvl.intranet'
LDAP_QUERY = 'uid={},ou=smile,ou=users,dc=smile,dc=fr'


def get_user_id_from_ldap(pentagram, ldap_url=LDAP_SERVER_URL,
                          ldap_query=LDAP_QUERY):
    """Get user id from pentagram.

    :pentagram: pentagram: string
    :returns: user_id: string

    """
    if not len(pentagram) == 5:
        LOGGER.error('Invalid user name, skipping...')
        return None
    try:
        ldap_server = ldap.initialize(ldap_url)
        ldap_server.simple_bind()
    except ldap.LDAPError:
        LOGGER.error('Error while connecting to LDAP server, skipping...')
        return None
    try:
        results = ldap_server.search_s(
            ldap_query.format(pentagram), ldap.SCOPE_SUBTREE,
            attrlist=['uidNumber'])
    except ldap.NO_SUCH_OBJECT:
        LOGGER.error('No match found, skipping...')
        return None
    if not len(results) == 1:
        LOGGER.error('Too many users matching, skipping...')
        return None
    _, arr = results[0]
    return arr['uidNumber'][0]
