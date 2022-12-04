from collections import defaultdict
from typing import Literal

from alive_progress import alive_bar
from bs4 import BeautifulSoup
from pydantic import validate_arguments

from ..collector.interface import AIOHTTPCollector, BaseCollector
from ..core.config import ExternalSourcesSettings
from ..db.postgres import PostgresWriter
from ..models import data_sources
from ..models.collector_model import CollectorResponse
from ..utils.helper import use_chunks
from .base_entities import BaseParser


class CyberleninkaParser(BaseParser):
    parser_type: str = "html.parser"

    def parse(self, page: str, format_: str) -> BeautifulSoup:
        return BeautifulSoup(page, format_)

    def parse_main_page(self, main_page: CollectorResponse) -> dict[str, list]:
        bs_main_page = self.parse(main_page.page_content, self.parser_type)
        catalog_of_scientific_articles = defaultdict(list)

        for part in ("half", "half-right"):
            self._get_catalogs_by_part(bs_main_page, part, catalog_of_scientific_articles)
        return catalog_of_scientific_articles

    def extract_humanitarian_sciences(
        self,
        main_page: CollectorResponse,
        base_url: str | None = None,
    ) -> data_sources.SectionCyberleninka:
        catalog_of_scientific_articles = self.parse_main_page(main_page)
        return data_sources.SectionCyberleninka(
            tags=tuple(
                data_sources.SectionCyberleninkaTag(
                    tag_name=tag_name,
                    tag_url=tag_url if base_url is None else f"{base_url}{tag_url}",
                )
                for tag_name, tag_url in catalog_of_scientific_articles["Гуманитарные науки"]
            ),
        )

    @validate_arguments
    def extract_page_pagination(
        self,
        resources: tuple[CollectorResponse, ...],
    ) -> data_sources.CyberleninkaPagesPagination:
        pagination = []
        for resource in resources:
            bs_resource = self.parse(resource.page_content, self.parser_type)
            last_link_url = bs_resource.find("ul", {"class": "paginator"})
            last_link_url = last_link_url.find("a", {"class": "icon"}).get("href")
            last_page = int(last_link_url.split("/")[-1])
            pagination.append(
                data_sources.CyberleninkaPagePagination(
                    request_url=resource.request_url,
                    page_last=last_page,
                ),
            )
        return data_sources.CyberleninkaPagesPagination(pages=tuple(pagination))

    @validate_arguments
    def parse_article(self, resource: CollectorResponse) -> data_sources.CyberleninkaArticle:
        bs_resource = self.parse(resource.page_content.replace("\n", ""), self.parser_type)

        return data_sources.CyberleninkaArticle(
            cyberleninka_id=resource.last_part_url,
            title=bs_resource.find("i", {"itemprop": "headline"}).text,
            authors=self._extract_author(bs_resource),
            publication_date=int(bs_resource.find("time", {"itemprop": "datePublished"}).text),
            science_magazine=self._extract_magazine(bs_resource),
            annotation=self._extract_annotation(bs_resource),
            article_text=bs_resource.find("div", {"itemprop": "articleBody"}).text.strip(),
            field_of_sciences=self._extract_field_of_sciences(bs_resource),
            keywords=self._extract_keywords(bs_resource),
            tags=self._extract_tags(bs_resource),
            similar_topics=self._extract_similar_topics(bs_resource),
            source_url=resource.request_url,
            pdf_url=f"{resource.request_url}/pdf",
        )

    @staticmethod
    def _extract_similar_topics(page: BeautifulSoup) -> tuple[data_sources.CyberleninkaArticleSimilarTopic, ...]:
        topics = page.select_one("body > div.content > div > span > div:nth-child(2) > div:nth-child(11) > div")
        similar_topics = []
        for topic in topics.find_all("li"):

            publication_date, *authors = topic.find("a").find("span").text.split("/")
            if not authors:
                continue
            authors = "".join(authors).strip()

            publication_date = int(publication_date.strip())
            authors = tuple(
                data_sources.CyberleninkaArticleAuthor(
                    name=author.strip(),
                )
                for author in authors.split(",")
            )

            similar_topics.append(
                data_sources.CyberleninkaArticleSimilarTopic(
                    name=topic.find("a").find("div").text,
                    cyberleninka_id=topic.find("a")["href"].split("/")[-1],
                    publication_date=publication_date,
                    authors=authors,
                ),
            )
        return tuple(similar_topics)

    @staticmethod
    def _extract_tags(page: BeautifulSoup) -> tuple[str, ...]:
        tags = page.find("div", {"class": "labels"}).findAll("div")
        return tuple(tag.text for tag in tags[1:])

    @staticmethod
    def _extract_keywords(page: BeautifulSoup) -> tuple[str, ...]:
        keywords = page.select(
            "body > div.content > div > span > div:nth-child(2) > div:nth-child(7) > div > i",
        )
        if keywords:
            return tuple(keyword.text for keyword in keywords[0].find_all("span"))

    @staticmethod
    def _extract_field_of_sciences(page: BeautifulSoup) -> str:
        return page.select(
            "body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half-right > ul > li > a",
        )[0].text

    @staticmethod
    def _extract_author(
        page: BeautifulSoup,
    ) -> tuple[data_sources.CyberleninkaArticleAuthor, ...]:
        description_text = page.find("div", {"class": "full abstract"})
        if description_text is None:
            authors = page.find("h2", {"class": "right-title"}).text.split("—")[-1]
            author_names = authors.strip().split(",")
        elif description_text.find("span") is None:
            author_names = page.find("h2", {"class": "right-title"}).text.split("—")[-1].split(",")
        else:
            author_names = description_text.find("span").text.split("—")[-1].strip().split(",")
        return tuple(data_sources.CyberleninkaArticleAuthor(name=name.strip()) for name in author_names)

    @staticmethod
    def _extract_annotation(page: BeautifulSoup) -> data_sources.CyberleninkaAnnotation | None:
        current_text = page.find_all("p", {"itemprop": "description"})
        if not current_text:
            return data_sources.CyberleninkaAnnotation(current_text=None, en_text=None)
        text = current_text[0].text
        en_text = current_text[-1].text
        return data_sources.CyberleninkaAnnotation(current_text=text, en_text=en_text)

    @staticmethod
    def _extract_magazine(page: BeautifulSoup) -> data_sources.CyberleninkaArticleScienceMagazine:
        magazine_bs = page.select(
            "body > div.content > div > span > div:nth-child(2) > div:nth-child(6) > div.half > span > a",
        )
        magazine_name = magazine_bs[0].text
        magazine_url = f"https://cyberleninka.ru{magazine_bs[0].get('href')}"
        return data_sources.CyberleninkaArticleScienceMagazine(name=magazine_name, url=magazine_url)

    @staticmethod
    def _extract_article_text(page: BeautifulSoup) -> str:
        return page.find("div", {"itemprop": "articleBody"}).text

    @staticmethod
    def _get_catalogs_by_part(
        main_page: BeautifulSoup,
        part: Literal["half", "half-right"],
        scientific_catalog: dict,
    ) -> dict[str, list]:
        letter: str | None = None

        for catalog in main_page.find("div", {"class": part}).findAll("li"):
            if catalog.get("class") == ["letter"]:
                letter = catalog.text
                continue

            topic = catalog.find("a")
            if topic:
                scientific_catalog[letter].append(
                    (topic.text, topic.get("href")),
                )

    def extract_articles_id(self, page: BeautifulSoup) -> tuple[str, ...]:
        return tuple(
            article.find("a").get("href").split("/")[-1]
            for article in page.find("ul", {"class": "list"}).find_all("li")
        )

    @staticmethod
    def articles_id2urls(id_: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(f"https://cyberleninka.ru/article/n/{article_id}" for article_id in id_)


class Cyberleninka:
    collector: BaseCollector = AIOHTTPCollector()
    settings: ExternalSourcesSettings = ExternalSourcesSettings()
    parser: BaseParser = CyberleninkaParser()
    writer: PostgresWriter = PostgresWriter()

    def __init__(self) -> None:
        self.base_url: str = self.settings.sources["cyberleninka"]

        if "/article" in self.base_url:
            self.origin_url = self.base_url.replace("/article", "")
        else:
            self.origin_url = self.base_url

    def get_main_page(self) -> CollectorResponse:
        return self.collector.execute_single_get_request(self.base_url)

    def get_humanitarian_sciences_links(self) -> data_sources.SectionCyberleninka:
        return self.parser.extract_humanitarian_sciences(self.get_main_page(), self.origin_url)

    def get_pages_from_tags(self, tags: data_sources.SectionCyberleninka) -> data_sources.CyberleninkaPagesPagination:
        urls = tuple(tag.tag_url for tag in tags.tags)
        collector_responses = self.collector.execute_get_requests(urls)
        return self.parser.extract_page_pagination(collector_responses)

    def get_articles_from_page(self, page: str) -> tuple[data_sources.CyberleninkaArticle, ...] | None:
        articles_urls = self.get_urls_from_page(page)

        ids = tuple(el.split("/")[-1] for el in articles_urls)
        exists_id = self.writer.check_rows_exists(table_name="public.demo_cyberleninka", rows_id=ids)
        valid_url = tuple(f"https://cyberleninka.ru/article/n/{el[0]}" for el in exists_id if not el[-1][0]["exists"])
        if not valid_url:
            return None

        return self.get_articles_from_urls(valid_url)

    def get_urls_from_page(self, page: str) -> tuple[str, ...]:
        bs_page = self.parser.parse(page, self.parser.parser_type)
        articles_id = self.parser.extract_articles_id(bs_page)
        return self.parser.articles_id2urls(articles_id)

    def get_articles_from_urls(self, urls: tuple[str, ...]) -> tuple[data_sources.CyberleninkaArticle, ...]:
        articles_responses = self.collector.execute_get_requests(urls)
        return tuple(
            self.parser.parse_article(article_response)
            for article_response in articles_responses
            if article_response is not None
        )

    def collect_articles_from_pages(self, pages: data_sources.CyberleninkaPagesPagination) -> None:
        chunk_size = 10
        urls = use_chunks(pages.all_pages_urls, chunk_size)
        for chunk_url in urls[525:]:
            page_responses = self.collector.execute_get_requests(chunk_url)

            for page_response in page_responses:
                articles = self.get_articles_from_page(page_response.page_content)
                if articles:
                    self.writer.write_demo_cyberleninka(articles)
