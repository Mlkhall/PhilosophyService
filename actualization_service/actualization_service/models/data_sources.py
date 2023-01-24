from uuid import UUID, uuid4
from typing import Union, Tuple, Dict
from datetime import datetime

from pydantic import AnyHttpUrl, Field, HttpUrl, PositiveInt
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class SectionCyberleninkaTag:
    """Humanitarian Sciences Cyberleninka Tag."""

    tag_name: str
    tag_url: Union[HttpUrl, AnyHttpUrl]


@dataclass(frozen=True)
class SectionCyberleninka:
    """Humanitarian Sciences."""

    tags: Tuple[SectionCyberleninkaTag, ...]

    @property
    def tags_names(self) -> Tuple[str, ...]:
        return tuple(tag.tag_name for tag in self.tags)

    @property
    def tags_urls(self) -> Tuple[HttpUrl, ...]:
        return tuple(tag.tag_url for tag in self.tags)


@dataclass(frozen=True)
class CyberleninkaPagePagination:
    """Cyberleninka Page."""

    request_url: Union[HttpUrl, AnyHttpUrl]
    page_last: PositiveInt

    @property
    def pages_urls(self) -> Tuple[HttpUrl, ...]:
        return tuple(f"{self.request_url}/{page}" for page in range(1, self.page_last + 1))


@dataclass(frozen=True)
class CyberleninkaPagesPagination:
    """Cyberleninka Pages."""

    pages: Tuple[CyberleninkaPagePagination, ...]

    @property
    def pages_urls(self) -> Tuple[HttpUrl, ...]:
        return tuple(page.request_url for page in self.pages)

    @property
    def pages_last(self) -> Tuple[PositiveInt, ...]:
        return tuple(page.page_last for page in self.pages)

    def get_generator_all_pages_urls(self):
        return (page_url for page in self.pages for page_url in page.pages_urls)

    @property
    def all_pages_urls(self) -> Tuple[HttpUrl, ...]:
        return tuple(self.get_generator_all_pages_urls())


@dataclass(frozen=True)
class CyberleninkaArticleOnPage:
    id_: Union[PositiveInt, str]
    title: str

    @property
    def url(self) -> HttpUrl:
        return f"https://cyberleninka.ru/article/n/{self.id_}"


@dataclass(frozen=True)
class CyberleninkaPageContent:
    articles: Tuple[CyberleninkaArticleOnPage, ...]
    page_url: Union[HttpUrl, AnyHttpUrl]


@dataclass(frozen=True)
class CyberleninkaArticleAuthor:
    name: str
    id_: Union[UUID, str] = Field(alias="id", default_factory=uuid4)

    @property
    def first_name(self) -> str:
        return self.name.split()[0]

    @property
    def last_name(self) -> str:
        return self.name.split()[-1]


@dataclass(frozen=True)
class CyberleninkaArticleScienceMagazine:
    name: str
    url: Union[HttpUrl, AnyHttpUrl]
    id_: Union[UUID, str] = Field(alias="id", default_factory=uuid4)


@dataclass(frozen=True)
class CyberleninkaArticleSimilarTopic:
    name: str
    cyberleninka_id: str
    publication_date: PositiveInt
    authors: Union[Tuple[CyberleninkaArticleAuthor, ...], None]


@dataclass(frozen=True)
class CyberleninkaAnnotation:
    current_text: Union[str, None]
    en_text: Union[str, None]


@dataclass(frozen=True)
class CyberleninkaArticle:
    cyberleninka_id: str
    title: str
    authors: Tuple[CyberleninkaArticleAuthor, ...]
    publication_date: PositiveInt
    science_magazine: CyberleninkaArticleScienceMagazine
    annotation: Union[CyberleninkaAnnotation, None]
    article_text: str
    field_of_sciences: str
    tags: Union[Tuple[str, ...], None]
    keywords: Union[Tuple[str, ...], None]
    similar_topics: Union[Tuple[CyberleninkaArticleSimilarTopic, ...], None]
    source_url: Union[HttpUrl, AnyHttpUrl]
    pdf_url: Union[HttpUrl, AnyHttpUrl]

    @property
    def postgresql_view(self) -> Dict:
        # def drop_bad_symbols(text: str) -> str:
        #     return text.replace("'", "`").replace('"', "`")

        return {
            "cyberleninka_id": self.cyberleninka_id,
            "title": self.title,
            "authors": ", ".join(author.name for author in self.authors),
            "publication_year": self.publication_date,
            "science_magazine_name": self.science_magazine.name,
            "science_magazine_url": str(self.science_magazine.url),
            "annotation": self.annotation.current_text
            if self.annotation.current_text is not None
            else "NULL",
            "annotation_en": self.annotation.en_text
            if self.annotation.en_text is not None
            else "NULL",
            "article_text":self.article_text if self.article_text is not None else "NULL",
            "field_of_sciences": self.field_of_sciences,
            "tags": (", ".join(self.tags) if self.tags is not None else "NULL"),
            "keywords": (", ".join(self.keywords) if self.keywords is not None else "NULL"),
            "similar_topics": (
                    ", ".join(
                        topic.name for topic in self.similar_topics if self.similar_topics is not None
                    )
            ),
            "source_url": str(self.source_url),
            "pdf_url": str(self.pdf_url),
        }
