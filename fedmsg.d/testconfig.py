config = {

    'hubs.consumer.enabled': True,
    # Production ready.
    'hubs.sqlalchemy.uri': 'sqlite:////var/tmp/hubs.db',

    'endpoints': {
        # TODO -- fill these out later...
    },

    'logging': dict(
        version=1,
        loggers=dict(
            hubs={
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["console"],
            },
        ),
    ),
}
