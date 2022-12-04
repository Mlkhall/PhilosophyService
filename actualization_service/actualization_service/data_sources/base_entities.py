from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class BaseParser(ABC):
    @abstractmethod
    def parse(self, page: str, format_: str) -> BeautifulSoup:
        pass
