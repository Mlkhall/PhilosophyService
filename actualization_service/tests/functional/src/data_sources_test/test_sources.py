from http import HTTPStatus

import pytest


@pytest.mark.asyncio
class TestCollectorSources:
    async def test_ping_sources(self, aiohttp_session_without_sll, web_hosts_fixture):
        for name_source_host in web_hosts_fixture:
            async with aiohttp_session_without_sll.get(web_hosts_fixture[name_source_host]) as response:
                assert response.status == HTTPStatus.OK

    async def test_cyberleninka(self, aiohttp_session, web_hosts_fixture):
        async with aiohttp_session.get(web_hosts_fixture["cyberleninka"]) as response:
            assert response.status == HTTPStatus.OK

    async def test_gtmarket(self, aiohttp_session, web_hosts_fixture):
        async with aiohttp_session.get(web_hosts_fixture["gtmarket"]) as response:
            assert response.status == HTTPStatus.OK

    async def test_philosophy_ru(self, aiohttp_session, web_hosts_fixture):
        async with aiohttp_session.get(web_hosts_fixture["philosophy"]) as response:
            assert response.status == HTTPStatus.OK

    async def test_journals(self, aiohttp_session_without_sll, web_hosts_fixture):
        async with aiohttp_session_without_sll.get(web_hosts_fixture["journals"]) as response:
            assert response.status == HTTPStatus.OK

    async def test_habr(self, aiohttp_session, web_hosts_fixture):
        async with aiohttp_session.get(web_hosts_fixture["habr"]) as response:
            assert response.status == HTTPStatus.OK
