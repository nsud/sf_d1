import sys

import requests

# Данные авторизации в API Trello
auth_params = {
    'key': "",  # необходимо добавить свой key
    'token': "" # необходимо добавить свой token
    }

base_url = "https://api.trello.com/1/{}"

board_id = ''   # необходимо добавить свой board_id


def columns():
    # Получим данные всех колонок на доске
    return requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params)


def read():
    # Получим данные всех колонок на доске:
    column_data = columns().json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(f"Колонка {column['name']} содержит {len(task_data)} тасков:")
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])


def create(name, column_name):
    # Проверям наличие задачи с таким именем в доске
    check_name(name, column_name)

    # Получим данные всех колонок на доске
    column_data = columns().json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params)
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            print(f"Задача {name} создана в колонке {column_name}")
            break


def check_name(name, column_name):
    # Получим данные всех колонок на доске
    column_data = columns().json()
    # Проверка совпадения названия задачи
    for column in column_data:
        cards = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for c in cards:
            if c['name'] == name:
                print(f'Задача с таким именем уже существует в колонке {column["name"]}')
                conf = input(f"Создать с таким же именем в колонке {column_name}? (Y/N): ")
                if conf.upper() != 'Y':
                    sys.exit()
                return


def create_col(name):

    params = {'name': name, 'pos': 'bottom', **auth_params}
    requests.post(base_url.format('boards') + '/' + board_id + '/lists', params=params).json()
    print(f"Колонка {name} создана")


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = columns().json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                task_id = task['id']
                break
        if task_id:
            break

            # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            break


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    # создать колонку
    elif sys.argv[1] == 'add':
        create_col(sys.argv[2])