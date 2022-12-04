from actualization_service.data_sources.cyberleninka import Cyberleninka


def main():
    source: Cyberleninka = Cyberleninka()
    links = source.get_humanitarian_sciences_links()
    pages = source.get_pages_from_tags(links)
    articles = source.collect_articles_from_pages(pages)
    print(articles)


if __name__ == "__main__":
    main()
