import os
from typing import Dict, Optional

from dotenv import dotenv_values

ENV_MAP: Dict[str, str] = {
    "dev": ".",
    "prod": "/app/storage",
    "staging": "/app/storage",
}


def get_configs() -> Dict[str, Optional[str]]:
    "Get the configuration from the .env files and environment variables"
    base_config = {
        # load default dev variables (non-sensitive, NOT gitignored)
        **dotenv_values(".env"),
        # override loaded values with environment variables
        **os.environ,
    }
    env: str = base_config.get("ENV", "dev") or "dev"
    env_path: str = base_config.get("ENV_PATH", "") or ENV_MAP.get(env, ".")
    if env not in ENV_MAP:
        env = "dev"
    if env_path not in ENV_MAP.values():
        env_path = ENV_MAP[env]
    base_config["ENV"] = env
    base_config["ENV_PATH"] = env_path
    config = {
        # load default vars (non-sensitive, NOT gitignored, environment var overridden)
        **base_config,
        # override with /dev/prod/staging variables
        **dotenv_values(f"{base_config['ENV_PATH']}/.env"),
        # load sensitive variables
        **dotenv_values(f"{base_config['ENV_PATH']}/.env.secret"),
        # override ALL loaded values with environment variables
        **os.environ,
    }
    return config
