Т.к. я не знаю Tornado и пока не собираюсь его учить, всё это будет переделано под Django (как только я его выучу).

Интерфейс чуть менее, чем полностью слизан с github, во-первых, интерфейс вообще не нужен, во-вторых, мне лень было искать нечто столь же простое и функциональное, в третьих - и так сойдет.

----------
# mysky_test
Тестовое задание mysky


С использованием Python 2 или 3 и фреймворка Tornado напишите веб-сервис со следующим функционалом

1. Логин и логаут пользователя
2. Только для залогиненных пользователей возможность загружать файлы PDF в сервис и смотреть уже загруженные в виде таблицы:  в первом столбце — логин пользователя, загрузившего файл; во втором — кликабельное имя файла, по клику на которое скачивается файл. (Достаточно сделать и загрузку, и список на одной странице.) Список отсортируйте по порядку загрузки файлов в сервис, начиная с самого раннего.
3. Загруженный в сервис PDF нужно разделить на отдельные страницы в формате PNG, которые вместе с исходным файлом должны также присутствовать в списке и скачиваться. Для рендеринга страниц из PDF можете использовать любой удобный модуль.
4. Если есть желание и время, то можете организовать "иерархию" файлов, чтобы каким-то образом была зафиксирована связь между PDF-файлом и созданными из него страницами.

В качестве базы данных используйте SQLite.
Вместе со ссылкой на код или кодом, напишите нам, как запускать ваш сервис.

# Установка и запуск
1. Используется >=python-3.5 и >=django-2.0
2. git clone https://github.com/Rashefort/mysky_test
3. Удовлетворить тем или иным способом содержимое requirements.txt.
4. Установить GraphicsMagic - http://www.graphicsmagick.org/download.html
5. Установить GhostScript - https://www.ghostscript.com/download/
6. Выполнить - manage.py runserver
7. Открыть в браузере http://127.0.0.1:8000
8. логин/пароль - admin/pazzword
