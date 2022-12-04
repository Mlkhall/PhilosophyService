import asyncio
from os.path import abspath, dirname, join

import pytest
import pytest_asyncio
import toml

CURRENT_DIR = dirname(abspath(__file__))


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config():
    return toml.load(join(CURRENT_DIR, "testdata/pytest_conf_data.toml"))


@pytest.fixture(scope="session")
def config_sources(config) -> dict[str, str]:
    return config["sources"]


@pytest.fixture(scope="session")
def config_sources_names(config_sources) -> tuple[str, ...]:
    return tuple(config_sources.keys())


@pytest.fixture(scope="session")
def config_sources_urls(config_sources) -> tuple[str, ...]:
    return tuple(config_sources.values())
