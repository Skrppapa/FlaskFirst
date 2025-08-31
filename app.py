from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#  Из библиотеки flask импортируем:

# класс Flask
# render_template для html шаблонов
# url_for для подключения статических фалов через шаблонизатор

app = Flask(__name__)   # Создаем экземпляр класса (создаем текущий экземпляр приложения) __name__ ссылается на app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # Конструкция ы которой мы указываем с какой БД будем работать
db = SQLAlchemy(app)    # Передаем именно имя приложения. Важно что бы перед этим БД была уже настроена как строкой выше


class Article(db.Model):    # Наследуем все от объекта db
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    intro = db.Column(db.String(300), nullable = False)
    text = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):                 # Функция говорит, что когда мы будем брать определенную запись из класса Article то нам будет выдаваться сама запись + ее id
        return '<Article %r>' % self.id


@app.route("/")        # @app.route("/") - Декоратор route сообщает браузеру какой URL запускает нашу функцию ("/" — это маршрут для главной страницы (корень сайта))
@app.route("/home")    # Ставлю еще один декоратор. При обращении к любому из этих адресов будет выводится функция ниже. Так можно на разные адреса вешать одно действие
def home():            # def home(): — Функция home, будет выполняться при запросе к этому адресу
    return render_template('index.html')

# В проекте для шаблонов html и css создаем папку templates по умолчанию Flask ищет шаблоны именно в папке с таким названием
# Аналогичная ситуация с папкой static для CSS
# render_template инструмент через который мы выводим шаблоны
# В пороекте применили наследование шаблонов. Код для наследования прописан в base.html. В остальных шаблонах наследуем код и заполняем блоки {% block Название блока %}{% endblock %}
# Для красивыо оформленных страниц использовали Bootstrap - CSS фреймворк с готовыми стилями

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/posts")   # Отображение списка статей
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()   # Article - моджель БД, проще - это наша БД. query() - метод который позволяет обратится как бы конкретно к нашей таблице
                                                                   # all() - выдает все записи
    return render_template('posts.html', articles = articles)      # articles = articles Передаем шаблон в котором будет список articles - то есть список всех постов. Первый articles это название можно было присвоить любое


@app.route("/posts/<int:id>")  # Детализация статьи
def post_details(id):
    article = Article.query.get(id)    # Функция get(id) просто получает запись из БД. Не обновляет/удаляет/перезаписывает
    return render_template('post_details.html', article = article)


# Добавление статьи
@app.route("/create-article", methods = ['POST', 'GET'])   # Что бы метод не только прямо переходил на шаблоны (то есть выполнял только GET) прописываем все методы с которыми он будет работать
def create_article():                                      # Так же в импортах прописываем request. request - Это контейнер в котором упакованы все данные которые мы послали на сервер.
    if request.method == 'POST':         # Если форма отправлена
        title = request.form['title']    # Поулдчаем данные из формы
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title = title, intro = intro, text = text) # Эта строка создает объект на основе класса Article который описывает таблицу в БД
                                                                     # Почему мы не берем данные из request и не записываем их напрямую в БД?
        try:                                                         # Это ORM подход. В нем мы работаем не с SQL напрямую, а с объектами, в данном случае с Python объектами
            db.session.add(article)                                  # То есть мы создаем объект из класса описывающего БД, вкладываем в него нужные данные из request
            db.session.commit()                                      # Затем SQLAlchemy автоматически преобразует объект в SQL команды и все раскладывает в БД
            return redirect('/posts')
        except:                                                      # В блоке try первая команда добавляет объект в БД, вторая коммитит - то есть записывает
            return 'При добавлении статьи произошла ошибка'          # db.session.add(article) Добавляем в сессию (подготовка к сохранению)
    else:                                                            # db.session.commit() теперь выполняем SQL INSERT в БД
        return render_template('create-article.html')


@app.route("/posts/<int:id>/delete")   # Удаление статьи
def post_delete(id):
    article = Article.query.get_or_404(id)   # Работает аналогично get() но в случае не нахождения id выдает 404. Это хорошая практика при удалении записи
    try:                                     # Конструкцию try exept нужно прописывать всегда когда мы работаем с БД - Хорошая практика!
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'При удалении статьи произошла ошибка'


@app.route("/posts/<int:id>/update", methods = ['POST', 'GET'])   #  Редактирование статьи
def post_update(id):
    article = Article.query.get(id)   # Нашили нужный объект
    if request.method == 'POST':
        article.title = request.form['title']   # Забираем данные из формы html и устанавливаем в поля
        article.intro = request.form['intro']
        article.text = request.form['text']
                                                # Создавать объект не нужно, забрали нужные данные и далее просто его перезаписали через commit
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При редактировании статьи произошла ошибка'
    else:

        return render_template('post_update.html', article=article)


# @app.route("/user/<string:name>/<int:id>")    # После пути user прописываем <> помещаем в них тип и что будем выводить
# def user(name, id):    # Функция принимает как раз параметры что указаны выше
#    return 'User page: ' + name + ' - ' + str(id)   # При адресе http://127.0.0.1:5000/user/Alex/23 Будет выведена наша строка




# ----------------------------------------------- Запуск приложения

if __name__ == '__main__':    # if __name__ == '__main__' - Конструкция для запуска сервера
    app.run(debug = True)     # app.run(debug=True) - run это метод класса Flask, который запускает встроенный веб-сервер Flask


# Активация окружения myenv\Scripts\activate
