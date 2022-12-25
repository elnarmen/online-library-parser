import json
import os
from more_itertools import chunked, divide
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

    books_descriptions = list(chunked(json.loads(books_descriptions_json), 20))
    pages_ammount = len(books_descriptions)
    for current_page, books_on_page in enumerate(books_descriptions, 1):
        print(list(chunked(books_on_page, 2)))  # 2
        rendered_page = template.render(books_on_page=list(chunked(books_on_page, 2)),
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

l = [
    [{'name': '53-я американская мечта', 'author': 'Салли Джейли', 'img_src': 'https://tululu.org/images/nopic.gif',
       'img_stat': '/static/images/nopic.gif',
       'book_path': '/home/elnar/projects/online_library_parser/attachments/books/53-я американская мечта.txt',
       'comments': ['Полнейший бред по моему мнению.',
                    'Вы можете долго искать смысл в этом рассказе, но так и не найти. В этом, наверное, и была цель автора.'],
       'genres': ['Научная фантастика']}, {'name': '6-я книга. Сражение за Бидруп.', 'author': 'Карр Алекс',
                                           'img_src': 'https://tululu.org/images/nopic.gif',
                                           'img_stat': '/static/images/nopic.gif',
                                           'book_path': '/home/elnar/projects/online_library_parser/attachments/books/6-я книга. Сражение за Бидруп..txt',
                                           'comments': [], 'genres': ['Научная фантастика']}],
    [
         {'name': '64-клеточный дурдом', 'author': 'Лейбер Фриц', 'img_src': 'https://tululu.org/images/nopic.gif',
          'img_stat': '/static/images/nopic.gif',
          'book_path': '/home/elnar/projects/online_library_parser/attachments/books/64-клеточный дурдом.txt',
          'comments': [
              'Заставляет задуматься- человек против мной машины или наоборот. Понравится любителям шахматных игр- книга для вас.'],
          'genres': ['Научная фантастика']}, {'name': '7-я книга. День Откровения', 'author': 'Карр Алекс',
                                              'img_src': 'https://tululu.org/images/nopic.gif',
                                              'img_stat': '/static/images/nopic.gif',
                                              'book_path': '/home/elnar/projects/online_library_parser/attachments/books/7-я книга. День Откровения.txt',
                                              'comments': [], 'genres': ['Научная фантастика']}],
    [
         {'name': '8-я книга. Полет Уригленны.', 'author': 'Карр Алекс',
          'img_src': 'https://tululu.org/images/nopic.gif', 'img_stat': '/static/images/nopic.gif',
          'book_path': '/home/elnar/projects/online_library_parser/attachments/books/8-я книга. Полет Уригленны..txt',
          'comments': [], 'genres': ['Научная фантастика']}]
]
