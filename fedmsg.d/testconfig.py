config = {

    'hubs.consumer.enabled': True,
    # Production ready.
    'hubs.sqlalchemy.uri': 'sqlite:////var/tmp/hubs.db',

    'endpoints': {
        "fedora-infrastructure": [
            "tcp://hub.fedoraproject.org:9940",
        ]
    },

    'datanommer.sqlalchemy.uri': 'postgres://postgres:laksjdf@127.0.0.1/datanommer',

    'fmn.url': 'https://apps.fedoraproject.org/notifications',

    # Some configuration for the rule processors
    "fmn.rules.utils.use_pkgdb2": False,
    "fmn.rules.utils.pkgdb2_api_url": "http://209.132.184.188/api/",
    "fmn.rules.cache": {
        "backend": "dogpile.cache.dbm",
        "expiration_time": 300,
        "arguments": {
            "filename": "/var/tmp/fmn-cache.dbm",
        },
    },
}
