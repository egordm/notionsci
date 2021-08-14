import logging

from notionsci.config import CONFIG_VERSION


def migrate(config: dict):
    logging.info(f'Migrating config from {config["version"]} to version {CONFIG_VERSION}')
    return config
