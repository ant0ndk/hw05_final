# hw05_final

Социальную сеть для публикации личных дневников.
Сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора.
Авторизованные пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
Автор может выбрать имя и уникальный адрес для своей страницы.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.

Проект реализован с использованием фреймворка django
Приложение "posts" покрыто тестами unitest

Запуск 
1. клонировать репозиторий     
```sh
    git clone https://github.com/ant0ndk/hw05_final.git
```
2. Создать вируальное окружение
```sh
    python -m venv venv
```
3. Запустить виртуальное окружение
    - для Windows
```sh
        source venv/Scripts/activate
```
    - для Mac и Linux
```sh
        source venv/bin/activate
```
4. Установить зависимости
```sh
    pip install -r requirements.txt
```
5. Запустить сервер Django
```sh
    python manage.py runserver
```
6. Сделать и запустить миграции
```sh
    python manage.py makemigrations
    python manage.py migrate
```
7. Создать суперпользователя
```
    python manage.py createsuperuser
```
8. Можно загрузить тестовые данные для проверки работоспособности проекта
```sh
    python manage.py loaddata dump.json
```
