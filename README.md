# 1. __Clone__
    git clone git@github.com:asssswv/test_task_yandex.git
# 2. __Installing all dependencies__
    pip install -r requirements.txt
# 3. Init DataBase
    pyton
    >>> from app import db
    >>> db.create_all()
# 4. Run server
    python app.py
    
# Описание
__Сервер представляет собой магазин в котором могут храниться разные товары и катогерии.__

__Можно добавлять товары/категории и изменять, также можно их удалять по ___id___.__
