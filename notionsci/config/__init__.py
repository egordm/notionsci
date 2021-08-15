import logging
import os
import sys

import yaml
from platformdirs import user_config_dir

from notionsci.config.constants import CONFIG_VERSION, APP_NAME, OVERRIDE_CONFIG_NAME, DEFAULT_PROFLE
from notionsci.config.migrations import migrate
from notionsci.config.structure import Config


def load_config() -> (Config, str):
    logging.basicConfig(level=logging.INFO)

    profile_arg = next(filter(lambda x: x.startswith("--profile="), sys.argv), None)
    if profile_arg:
        sys.argv.remove(profile_arg)
        profile_arg = profile_arg.replace("--profile=", "")

    profile = profile_arg or os.getenv("PROFILE", None) or DEFAULT_PROFLE
    config_name = f"{profile}.yml"

    # Determine correct config location
    if os.path.exists(OVERRIDE_CONFIG_NAME):
        config_path = OVERRIDE_CONFIG_NAME
        logging.info(
            f"Using overridden {OVERRIDE_CONFIG_NAME} in the current directory"
        )
    else:
        config_path = os.path.join(user_config_dir(APP_NAME), config_name)
        if not os.path.exists(config_path):
            logging.info(
                f'No {profile} config detected.\n' \
                f"Creating default config in: {config_path}\n" \
                f"Please update the api tokens"
            )
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            Config().save(config_path)
            exit(0)

    # Try loading overridden config
    with open(config_path, 'r') as f:
        config_raw = yaml.safe_load(f)
    config_raw = config_raw or {}

    # Run migrations on config
    write = False
    if config_raw.get('version', 0) < CONFIG_VERSION:
        write = True
        config_raw = migrate(config_raw)

    config: Config = Config.from_dict(config_raw)

    # Write migrated config
    if write:
        with open(config_path, 'w') as f:
            config.dump_yaml(f)

    return config, config_path


c, cp = load_config()
config: Config = c
config_path: str = cp


def write_config(config: Config):
    with open(config_path, 'w') as f:
        config.dump_yaml(f)
