config = {

    'hubs.consumer.enabled': True,
    # Production ready.
    'hubs.sqlalchemy.uri': 'sqlite:////var/tmp/hubs.db',

    'endpoints': {
        "fedora-infrastructure": [
            "tcp://hub.fedoraproject.org:9940",
        ]
    },
}
