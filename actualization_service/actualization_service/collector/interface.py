import asyncio
from abc import ABC, abstractmethod
from http import HTTPStatus

import aiohttp
from loguru import logger

from ..core.config import COLLECTOR_SETTINGS
from ..models.collector_model import CollectorResponse
from ..utils.stability import async_backoff


class BaseCollector(ABC):
    @staticmethod
    @abstractmethod
    def fetch(session: aiohttp.ClientSession, url: str) -> CollectorResponse:
        pass

    @abstractmethod
    def _get_request(self, url: str) -> CollectorResponse:
        pass

    @abstractmethod
    def execute_single_get_request(self, url: str) -> CollectorResponse:
        pass

    @abstractmethod
    def execute_get_requests(
        self,
        urls: tuple[str, ...],
    ) -> tuple[CollectorResponse, ...]:
        pass


class AIOHTTPCollector(BaseCollector):
    def __init__(self, timeout: int = COLLECTOR_SETTINGS.TIMEOUT) -> None:

        self.session_timeout = aiohttp.ClientTimeout(
            total=None,
            sock_connect=timeout,
            sock_read=timeout,
        )

    @staticmethod
    @async_backoff(
        start_sleep_time=COLLECTOR_SETTINGS.START_SLEEP_TIME,
        factor=COLLECTOR_SETTINGS.FACTOR,
        border_sleep_time=COLLECTOR_SETTINGS.BORDER_TIME_SLEEP,
    )
    async def fetch(session: aiohttp.ClientSession, url: str) -> CollectorResponse:
        async with session.get(url) as response:
            if response.status == HTTPStatus.OK:
                logger.success(f"Request to {url} was successful!")
                return CollectorResponse(
                    status=response.status,
                    page_content=await response.text(),
                    request_url=url,
                )
            elif response.status == HTTPStatus.NOT_FOUND:
                logger.error(f"Request to {url} was not found!")
                return None
            logger.error(f"Request to {url} was failed! Status code: {response.status}")
            raise aiohttp.ClientError(f"Response status is {response.status}")

    async def _get_request(
        self,
        url: str,
    ) -> CollectorResponse:
        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            return await self.fetch(session, url)

    def execute_single_get_request(self, url: str) -> CollectorResponse:
        return asyncio.run(self._get_request(url))

    def execute_get_requests(self, urls: tuple[str, ...]) -> tuple[CollectorResponse, ...]:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        async_requests = (self._get_request(url) for url in urls)
        return tuple(event_loop.run_until_complete(asyncio.gather(*async_requests)))
