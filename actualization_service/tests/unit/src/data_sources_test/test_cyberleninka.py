from collections import defaultdict

import nest_asyncio
import pytest
import validators
from bs4 import BeautifulSoup

from actualization_service.data_sources.cyberleninka import (
    Cyberleninka,
    CyberleninkaParser,
)
from actualization_service.models import collector_model, data_sources

nest_asyncio.apply()


@pytest.mark.asyncio
class TestCyberleninka:
    source: Cyberleninka = Cyberleninka()

    async def test_get_main_page(self):
        assert Cyberleninka().get_main_page() is not None

    async def test_get_humanitarian_sciences_links(self):
        humanitarian_sciences_links = self.source.get_humanitarian_sciences_links()
        assert humanitarian_sciences_links is not None
        assert isinstance(humanitarian_sciences_links, data_sources.SectionCyberleninka)
        assert isinstance(humanitarian_sciences_links.tags, tuple)
        assert isinstance(humanitarian_sciences_links.tags[0], data_sources.SectionCyberleninkaTag)
        assert humanitarian_sciences_links.tags_urls is not None
        assert isinstance(humanitarian_sciences_links.tags_urls, tuple)

    async def test_get_pages_from_tags(self):
        pages = self.source.get_pages_from_tags(self.source.get_humanitarian_sciences_links())
        assert pages is not None
        assert isinstance(pages, data_sources.CyberleninkaPagesPagination)
        assert isinstance(pages.pages, tuple)
        assert isinstance(pages.pages[0], data_sources.CyberleninkaPagePagination)

    async def test_get_articles_from_pages(self):

        pages = self.source.get_pages_from_tags(self.source.get_humanitarian_sciences_links())
        response = self.source.collector.execute_single_get_request(pages.pages[0].pages_urls[0])
        articles = self.source.get_articles_from_page(response.page_content)
        assert articles is not None
        assert isinstance(articles, tuple)
        assert isinstance(articles[0], data_sources.CyberleninkaArticle)
        assert all(isinstance(article, data_sources.CyberleninkaArticle) for article in articles)

    async def test_collect_articles_from_pages(self):
        pages = self.source.get_pages_from_tags(self.source.get_humanitarian_sciences_links())
        articles = self.source.collect_articles_from_pages(pages)
        assert articles is None


@pytest.mark.asyncio
class TestCyberleninkaParser:
    source: Cyberleninka = Cyberleninka()
    parser: CyberleninkaParser = CyberleninkaParser()

    async def test_parse_main_page(self):
        main_page = self.source.get_main_page()
        parsed_main_page = self.parser.parse_main_page(main_page)
        types = {
            "Медицинские науки",
            "Естественные и точные науки",
            "Техника и технологии",
            "Гуманитарные науки",
            "Сельскохозяйственные науки",
            "Социальные науки",
        }
        assert isinstance(parsed_main_page, defaultdict)
        assert all(source in types for source in parsed_main_page)

    async def test_parse(self):
        main_page = self.source.get_main_page()
        assert main_page is not None
        assert isinstance(self.parser.parse(main_page.page_content, self.parser.parser_type), BeautifulSoup)
        assert isinstance(self.parser.parse(main_page.page_content, "html.parser"), BeautifulSoup)

    async def test_extract_page_pagination(self):
        section = self.source.get_humanitarian_sciences_links()
        urls = tuple(tag.tag_url for tag in section.tags)
        collector_responses = self.source.collector.execute_get_requests(urls)
        pagination_of_pages = self.parser.extract_page_pagination(collector_responses)
        assert pagination_of_pages is not None
        assert isinstance(pagination_of_pages, data_sources.CyberleninkaPagesPagination)
        assert isinstance(pagination_of_pages.pages, tuple)
        assert isinstance(pagination_of_pages.all_pages_urls, tuple)

    async def test_parse_article(self):
        example_article_url = (
            "https://cyberleninka.ru/article/n/puti-i-puty-kritiki-o-sovremennom-sostoyanii"
            "-izucheniya-literatur-malochislennyh-narodov-severa-i-sibiri"
        )
        article_response = self.source.collector.execute_single_get_request(example_article_url)

        article = self.parser.parse_article(article_response)
        assert article is not None
        assert article.source_url == example_article_url
        assert (
            article.title == "Пути и путы критики: о современном состоянии изучения литератур малочисленных "
            "народов Севера и Сибири"
        )

        assert article.authors[0].name == "Хазанкович Юлия Геннадьевна"
        assert article.publication_date == 2009
        assert article.science_magazine.name == "Сибирский филологический журнал"
        if article.tags is not None:
            assert article.tags == ("Scopus", "ВАК", "RSCI", "ESCI")

        if article.keywords is not None:
            assert article.keywords == (
                "народы севера и сибири".upper(),
                "литература".upper(),
                "peoples of siberia and the north".upper(),
                "literature".upper(),
            )

    async def test_articles_id2urls(self):
        links = self.source.get_humanitarian_sciences_links()
        pages = self.source.get_pages_from_tags(links)
        test_url = pages.pages[0].pages_urls[0]
        response = self.source.collector.execute_single_get_request(test_url)
        page = self.parser.parse(response.page_content, self.parser.parser_type)
        articles_id = self.parser.extract_articles_id(page)
        articles_urls = self.parser.articles_id2urls(articles_id)
        assert articles_urls is not None
        assert isinstance(articles_urls, tuple)
        assert isinstance(articles_urls[0], str)
        assert len(articles_urls) == len(articles_id)
        assert all(map(validators.url, articles_urls))

    async def test_extract_articles_id(self):
        links = self.source.get_humanitarian_sciences_links()
        pages = self.source.get_pages_from_tags(links)
        test_url = pages.pages[0].pages_urls[0]
        response = self.source.collector.execute_single_get_request(test_url)
        page = self.parser.parse(response.page_content, self.parser.parser_type)
        articles_id = self.parser.extract_articles_id(page)
        assert articles_id is not None
        assert isinstance(articles_id, tuple)
        assert isinstance(articles_id[0], str)
