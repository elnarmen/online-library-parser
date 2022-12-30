import json
import os
import numpy
from environs import Env
from more_itertools import chunked
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Env()
env.read_env()
PATH = env('PATH_TO_DESCRIPTIONS', default='attachments/books_descriptions.json')
BOOKS_ON_PAGE = 20
NUMBER_OF_COLUMNS = 2


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open(PATH, 'r') as file:
        books_descriptions_json = json.load(file)
    books_descriptions = list(chunked(books_descriptions_json, BOOKS_ON_PAGE))
    pages_amount = len(books_descriptions)
    for current_page, books_on_page in enumerate(books_descriptions, 1):
        left_col, right_col = numpy.array_split(books_on_page, 2)
        rendered_page = template.render(
            left_col=left_col,
            right_col=right_col,
            pages_amount=pages_amount,
            current_page=current_page,
            zip=zip
        )
        folder = 'pages'
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f'index{current_page}.html'), 'w', encoding='utf8') as file:
            file.write(rendered_page)

def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()