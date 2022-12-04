import time

import aiohttp
import nest_asyncio
import pytest

from actualization_service.collector.interface import AIOHTTPCollector
from actualization_service.core.config import COLLECTOR_SETTINGS
from actualization_service.models.collector_model import CollectorResponse

nest_asyncio.apply()


@pytest.mark.asyncio
class TestAIOHTTPCollector:
    collector: AIOHTTPCollector = AIOHTTPCollector()

    async def test_fetch(self, config):
        current_url = config["test-urls"]["valid_url"]
        async with aiohttp.ClientSession() as session:
            assert isinstance(await self.collector.fetch(session, current_url), CollectorResponse)

    async def test_get_request(self, config):
        current_url = config["test-urls"]["valid_url"]
        assert await self.collector._get_request(current_url) is not None

    async def test_execute_single_get_request(self, config):
        current_url = config["test-urls"]["valid_url"]
        response = self.collector.execute_single_get_request(current_url)
        assert response is not None
        assert isinstance(response, CollectorResponse)
        assert isinstance(response.status, int)
        assert response.request_url == current_url
        assert isinstance(response.page_content, str)

    async def test_execute_get_requests(self, config):
        current_url = config["test-urls"]["valid_url"]
        url4requests = (current_url,) * 4
        collector_responses = self.collector.execute_get_requests(url4requests)
        assert collector_responses is not None
        assert isinstance(collector_responses, tuple)
        assert len(collector_responses) == len(url4requests)
        assert all(isinstance(response, CollectorResponse) for response in collector_responses)

    async def test_bad_request(self, config):
        current_url = config["test-urls"]["bad_url"]
        with pytest.raises((aiohttp.ClientError, ValueError)):
            await self.collector._get_request(current_url)

    async def test_backoff(self, config):
        current_url = config["test-urls"]["bad_url"]
        time_start = time.time()
        with pytest.raises(ValueError):
            await self.collector._get_request(current_url)
        time_end = time.time()

        assert time_end - time_start > COLLECTOR_SETTINGS.BORDER_TIME_SLEEP
