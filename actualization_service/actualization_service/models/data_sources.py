from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, Field, HttpUrl, PositiveInt
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class SectionCyberleninkaTag:
    """Humanitarian Sciences Cyberleninka Tag."""

    tag_name: str
    tag_url: HttpUrl | AnyHttpUrl


@dataclass(frozen=True)
class SectionCyberleninka:
    """Humanitarian Sciences."""

    tags: tuple[SectionCyberleninkaTag, ...]

    @property
    def tags_names(self) -> tuple[str, ...]:
        return tuple(tag.tag_name for tag in self.tags)

    @property
    def tags_urls(self) -> tuple[HttpUrl, ...]:
        return tuple(tag.tag_url for tag in self.tags)


@dataclass(frozen=True)
class CyberleninkaPagePagination:
    """Cyberleninka Page."""

    request_url: HttpUrl | AnyHttpUrl
    page_last: PositiveInt

    @property
    def pages_urls(self) -> tuple[HttpUrl, ...]:
        return tuple(f"{self.request_url}/{page}" for page in range(1, self.page_last + 1))


@dataclass(frozen=True)
class CyberleninkaPagesPagination:
    """Cyberleninka Pages."""

    pages: tuple[CyberleninkaPagePagination, ...]

    @property
    def pages_urls(self) -> tuple[HttpUrl, ...]:
        return tuple(page.request_url for page in self.pages)

    @property
    def pages_last(self) -> tuple[PositiveInt, ...]:
        return tuple(page.page_last for page in self.pages)

    def get_generator_all_pages_urls(self):
        return (page_url for page in self.pages for page_url in page.pages_urls)

    @property
    def all_pages_urls(self) -> tuple[HttpUrl, ...]:
        return tuple(self.get_generator_all_pages_urls())


@dataclass(frozen=True)
class CyberleninkaArticleOnPage:
    id_: PositiveInt | str
    title: str

    @property
    def url(self) -> HttpUrl:
        return f"https://cyberleninka.ru/article/n/{self.id_}"


@dataclass(frozen=True)
class CyberleninkaPageContent:
    articles: tuple[CyberleninkaArticleOnPage, ...]
    page_url: HttpUrl | AnyHttpUrl


@dataclass(frozen=True)
class CyberleninkaArticleAuthor:
    name: str
    id_: UUID | str = Field(alias="id", default_factory=uuid4)

    @property
    def first_name(self) -> str:
        return self.name.split()[0]

    @property
    def last_name(self) -> str:
        return self.name.split()[-1]


@dataclass(frozen=True)
class CyberleninkaArticleScienceMagazine:
    name: str
    url: HttpUrl | AnyHttpUrl
    id_: UUID | str = Field(alias="id", default_factory=uuid4)


@dataclass(frozen=True)
class CyberleninkaArticleSimilarTopic:
    name: str
    cyberleninka_id: str
    publication_date: PositiveInt
    authors: tuple[CyberleninkaArticleAuthor, ...] | None


@dataclass(frozen=True)
class CyberleninkaAnnotation:
    current_text: str | None
    en_text: str | None


@dataclass(frozen=True)
class CyberleninkaArticle:
    cyberleninka_id: str
    title: str
    authors: tuple[CyberleninkaArticleAuthor, ...]
    publication_date: PositiveInt
    science_magazine: CyberleninkaArticleScienceMagazine
    annotation: CyberleninkaAnnotation | None
    article_text: str
    field_of_sciences: str
    tags: tuple[str, ...] | None
    keywords: tuple[str, ...] | None
    similar_topics: tuple[CyberleninkaArticleSimilarTopic, ...] | None
    source_url: HttpUrl | AnyHttpUrl
    pdf_url: HttpUrl | AnyHttpUrl
    id_: UUID | str = Field(alias="id", default_factory=uuid4)

    @property
    def postgresql_view(self) -> dict:
        def drop_bad_symbols(text: str) -> str:
            return text.replace("'", "`").replace('"', "`")

        return {
            "id": str(self.id_),
            "cyberleninka_id": self.cyberleninka_id,
            "title": drop_bad_symbols(self.title),
            "authors": drop_bad_symbols(", ".join(author.name for author in self.authors)),
            "publication_year": self.publication_date,
            "science_magazine_name": drop_bad_symbols(self.science_magazine.name),
            "science_magazine_url": str(self.science_magazine.url),
            "annotation": drop_bad_symbols(self.annotation.current_text)
            if self.annotation.current_text is not None
            else "NULL",
            "annotation_en": drop_bad_symbols(self.annotation.en_text)
            if self.annotation.en_text is not None
            else "NULL",
            "article_text": drop_bad_symbols(self.article_text) if self.article_text is not None else "NULL",
            "field_of_sciences": drop_bad_symbols(self.field_of_sciences),
            "tags": (drop_bad_symbols(", ".join(self.tags)) if self.tags is not None else "NULL"),
            "keywords": (drop_bad_symbols(", ".join(self.keywords)) if self.keywords is not None else "NULL"),
            "similar_topics": (
                drop_bad_symbols(
                    ", ".join(
                        drop_bad_symbols(topic.name) for topic in self.similar_topics if self.similar_topics is not None
                    )
                )
            ),
            "source_url": str(self.source_url),
            "pdf_url": str(self.pdf_url),
        }
