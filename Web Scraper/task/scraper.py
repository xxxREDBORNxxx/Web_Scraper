import os
import sys
import string
import requests

from bs4 import BeautifulSoup

from requests.exceptions import RequestException


class InvalidResource(Exception):
    pass


class WebScraper:

    def __init__(self, url: str, type_articles: str, path: str):
        self.url = url
        self.type_articles = type_articles
        self.path = path
        self.links_articles = []
        self.punctuation_marks = [a for a in string.punctuation]

    def articles_scraper(self):

        response = self.__get_response(self.url)
        soup = self.__get_soup(response)
        self.get_links_articles(soup)

        for link in self.links_articles:
            response_link = self.__get_response(link)
            soup_link = self.__get_soup(response_link)
            content = self.get_content(soup_link)
            file_name = self.get_file_name(self.get_title(soup_link))

            file_path = os.path.join(self.path, file_name)
            self.save_txt_page_content(file_path, content)
            # self.__print_result('Saved all articles.')

    def get_links_articles(self, soup):
        article_links = soup.find_all('span', {'class': 'c-meta__type'}, text=self.type_articles)

        for article in article_links:
            article_tags_data = article.find_parent('article')
            article_tag = article_tags_data.find('a', {'data-track-action': 'view article'})
            link_article = article_tag.attrs.get('href')
            self.links_articles.append(f"https://www.nature.com{link_article}")

    def __check_request(self, adr):
        try:
            response = requests.get(adr, headers={'Accept-Language': 'en-US,en;q=0.5'})
        except RequestException:
            self.__print_result('Invalid quote resource!')
            sys.exit()
        else:
            try:
                self.__check_status_code(response)
            except InvalidResource as err:
                self.__print_result(err)
                sys.exit()
        return response

    def __get_response(self, adr):
        return self.__check_request(adr)

    @staticmethod
    def save_txt_page_content(file_name, data):
        with open(file_name, 'w', encoding='UTF-8') as text_content:
            text_content.write(data)
            # self.__print_result(f"Content {self.type_articles} saved: {file_name}")

    @staticmethod
    def get_content(soup_link):
        return soup_link.find('div', class_='c-article-body u-clearfix').text.rstrip()

    def get_file_name(self, title):
        set_edited_name = [a for a in title if a not in self.punctuation_marks]
        title = f"{(''.join(set_edited_name)).replace(' ', '_')}.txt"
        return title.replace('__', '_')

    @staticmethod
    def get_title(soup):
        return soup.find('h1', {'class': "c-article-magazine-title"}).text.strip()

    @staticmethod
    def __get_soup(response):
        return BeautifulSoup(response.content, 'html.parser')

    @staticmethod
    def __print_result(message):
        print(message)

    @staticmethod
    def __get_status_code(response):
        return response.status_code

    def __check_status_code(self, response):
        status_code = self.__get_status_code(response)
        if status_code not in range(200, 400):
            raise InvalidResource(f"The URL returned {status_code}!")


url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020&page='

pages_amount = int(input())
type_ = input()

for page_num in range(1, pages_amount + 1):
    folder_name = f'Page_{page_num}'
    path = os.path.join(os.getcwd(), folder_name)
    os.mkdir(path)
    adr = f"{url}{page_num}"
    WebScraper(adr, type_, path).articles_scraper()
print('Saved all articles.')
