from hashlib import sha256

from six.moves.urllib_parse import urlencode


def username2avatar(username, s=312):
    query = urlencode({
        'd': 'retro',
        's': s,
    })
    openid = 'http://%s.id.fedoraproject.org/' % username
    hash = sha256(openid.encode('utf-8')).hexdigest()
    avatar = "https://seccdn.libravatar.org/avatar/%s?%s" % (hash, query)
    return avatar


def commas(numeric):
    return "{:,}".format(numeric)
