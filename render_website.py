import json
import os
from more_itertools import chunked, chunked_even
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open("attachments/books_descriptions.json", "r") as file:
        books_descriptions_json = file.read()

    books_descriptions = list(chunked_even(json.loads(books_descriptions_json), 20))
    pages_ammount = len(books_descriptions)
    for current_page, books_on_page in enumerate(books_descriptions, 1):
        last_book = None
        if len(books_on_page) % 2:
            last_book = books_on_page[-1]
            books_on_page = books_on_page[:-1]
        rendered_page = template.render(
            books_on_page=chunked(books_on_page, 2),
            last_book=last_book,
            pages_ammount=pages_ammount,
            current_page=current_page
        )
        path = 'pages'
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f'index{current_page}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')


