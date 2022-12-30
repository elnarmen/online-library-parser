import os
import argparse
import time
import pathlib
import requests
import json
import pathvalidate
from environs import Env
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit

PATH = pathlib.Path.cwd() / 'attachments'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError()


def get_books_urls_on_page(soup_of_category_page, base_url):
    books_urls = [urljoin(base_url, book_card.select('a')[1]['href'])
                  for book_card in soup_of_category_page.select('.d_book')]
    return books_urls


def get_last_page_num(soup_of_category_page):
    return int(soup_of_category_page.select('.npage')[5].text)


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def download_txt(url, book_name, base_path, folder='books/') -> str:
    dest_folder = pathlib.Path(base_path)
    path = pathlib.Path(dest_folder / folder / f'{book_name}.txt')
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)


def get_text_download_url(book_page_soup, book_page_url):
    selector = 'table.d_book tr a[href^="/txt"]'
    url = urljoin(book_page_url,
                  book_page_soup.select_one(selector).get('href'))
    return url


def download_img(img_url, base_path, folder='images/'):
    dest_folder = pathlib.Path(base_path)
    path = dest_folder / folder / urlsplit(img_url).path.split('/')[-1]
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(path, 'wb') as file:
        file.write(response.content)


def write_books_descriptions(books_descriptions, base_path):
    descriptions_folder = pathlib.Path(base_path)
    path = descriptions_folder / 'books_descriptions.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(descriptions_folder, 'books_descriptions.json'),
              'w') as write_file:
        json.dump(books_descriptions, write_file, indent=4, ensure_ascii=False)


def parse_book_page(book_page_soup, book_page_url):
    book_name, author = book_page_soup.select_one('h1').text.split('::')
    valid_book_name = pathvalidate.sanitize_filename(book_name).strip()
    short_img_url = book_page_soup.select_one('.bookimage img').get('src')
    img_src = urljoin(book_page_url, short_img_url)
    img = f'/attachments/images/{urlsplit(img_src).path.split("/")[-1]}'

    book_descriptions = {

        'name': valid_book_name,

        'author': author.strip(),

        'img_src': img_src,

        'img': img,

        'book_path':
            os.path.join('attachments', os.path.join('books', f'{valid_book_name}.txt')),

        'comments': [comment.select_one('.black').text
                     for comment in book_page_soup.select('.texts')],

        'genres': [genre.text for genre in
                   book_page_soup.select('span.d_book a')]
    }

    return book_descriptions


def validate_args(args):
    for arg in args:
        if arg < 1:
            raise ValueError('Введите число больше 0')


def create_parser(default_end_page):
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги '
                    'из электронной библиотеки "tululu.org"'
    )
    parser.add_argument(
        '-s', '--start_page',
        type=int,
        default=default_end_page - 1,
        help='номер стартовой для скачивания страницы - целое число > 0'
    )
    parser.add_argument(
        '-e', '--end_page',
        default=default_end_page,
        type=int,
        help='номер последней для скачивания страницы - целое число > 0'
    )
    parser.add_argument(
        '--dest_folder',
        type=str,
        default=PATH,
        help='путь к каталогу для загрузки книг, их обложек и описаний',
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
        default=False,
        help='не скачивать изображения',
    ),
    parser.add_argument(
        '--skip_txt',
        help='не скачивать книги',
        action='store_true',
        default=False
    ),
    parser.add_argument(
        '--json_path',
        help='указать свой путь к *.json файлу с результатами',
        type=str,
        default=PATH
    )
    return parser


def main():
    env = Env()
    env.read_env()

    category_id = env.int('CATEGORY_ID', default=55)

    end_page = \
        get_last_page_num(get_soup(f'https://tululu.org/l{category_id}/'))

    parser = create_parser(end_page)
    namespace = parser.parse_args()


    validate_args([namespace.start_page, namespace.end_page])
    start_page, end_page = namespace.start_page, namespace.end_page
    all_books_urls = []
    books_descriptions = []

    for page_id in range(start_page, end_page):
        while True:
            try:
                category_page_url = \
                    f'https://tululu.org/l{category_id}/{page_id}/'
                soup_of_category_page = get_soup(category_page_url)
                all_books_urls.extend(
                    get_books_urls_on_page(soup_of_category_page,
                                           category_page_url)
                )
                break
            except requests.exceptions.HTTPError:
                print('Страница или категория отсутствует')
                break
            except requests.exceptions.ConnectionError as err:
                print(str(err),
                      'Не удалось установить соединение с сервером. '
                      'Проверьте подключение к интернету.'
                      'Повторная попытка через 10 сек')
                time.sleep(10)

    for book_page_url in all_books_urls:
        while True:
            book_page_soup = get_soup(book_page_url)
            description = parse_book_page(book_page_soup, book_page_url)
            book_name = description['name']
            img_url = description['img_src']
            try:
                if not namespace.skip_txt:
                    download_url = get_text_download_url(book_page_soup,
                                                         book_page_url)
                    download_txt(download_url, book_name, namespace.dest_folder)
                if not namespace.skip_imgs:
                    download_img(img_url, namespace.dest_folder)

            except (AttributeError, requests.exceptions.HTTPError):
                print(f'книга {book_name} отсутствует '
                      f'или недоступна для скачивания')
                break
            except requests.exceptions.ConnectionError as err:
                print(str(err),
                      'Не удалось установить соединение с сервером. '
                      'Проверьте подключение к интернету.'
                      'Повторная попытка через 10 сек')
                time.sleep(10)
            except:
                books_descriptions.append(description)
                break
            else:
                books_descriptions.append(description)
                break

    write_books_descriptions(books_descriptions, namespace.json_path)


if __name__ == '__main__':
    main()
