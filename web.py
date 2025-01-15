from bson import ObjectId
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from pymongo import MongoClient, errors
import os
import random
from main import getScribertEmbedings


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Rastgele bir secret key oluştur

login_manager = LoginManager(app)



# MongoDB'ye bağlan
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()  # Sunucunun çalışıp çalışmadığını kontrol et
    db = client['Yazlab2_3']
    users_collection = db['users']
    articles_collection = db['articles']
except errors.ServerSelectionTimeoutError as err:
    print("MongoDB bağlantı hatası:", err)
    raise SystemExit("MongoDB bağlantısı kurulamadı. Lütfen sunucunun çalıştığından emin olun.")


from flask_login import UserMixin, login_user, logout_user, login_required

# Kullanıcı sınıfı tanımlama
class User(UserMixin):
    def __init__(self, user_id, username, interests=None, clicked_articles=None):
        self.id = user_id  # Flask-Login'in beklediği 'id' niteliği
        self.username = username
        self.interests = interests or []
        self.clicked_articles = clicked_articles or []

    def get_id(self):
        return str(self.id)  # MongoDB'deki _id'yi dize olarak döndür


# Kullanıcı yükleyici
@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(
            user_data['_id'],
            user_data['username'],
            user_data.get('interests', []),
            user_data.get('clicked_articles', [])
        )
    return None

def get_user_interests(username):
    user_data = users_collection.find_one({'username': username})
    if user_data:
        return user_data.get('interests', [])
    return []

def select_initial_recommendations():
    if current_user and current_user.is_authenticated:
        user_interests = get_user_interests(current_user.username)
        all_articles = list(articles_collection.find())
        initial_recommendations = []

        for article in all_articles:
            article_keys = article.get('keys', [])
            common_interests = set(user_interests) & set(article_keys)
            
            if common_interests:
                article['common_interests'] = list(common_interests)
                initial_recommendations.append(article)

        for article in all_articles:
            if article in initial_recommendations:
                continue

            article_keys = article.get('keys', [])
            common_interests = []
            for interest in user_interests:
                interest_words = interest.split()
                for word in interest_words:
                    if any(word in key for key in article_keys):
                        common_interests.append(word)

            if common_interests:
                article['common_interests'] = common_interests
                initial_recommendations.append(article)

        return initial_recommendations
    else:
        return []



@app.route('/')
def index():
    try:
        username = None
        initial_recommendations = []
        all_scribert_recommendations = []
        all_fasttext_recommendations = []
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                username = user_data['username']
                clicked_articles = user_data.get('clicked_articles', [])
                if clicked_articles:
                    for clicked_article in clicked_articles:
                        scribert_recommendations, fasttext_recommendations = getScribertEmbedings(clicked_article)

                        scribert_recommendations_with_ids = [
                            articles_collection.find_one({'filename': rec['filename']})
                            for rec in scribert_recommendations
                        ]

                        fasttext_recommendations_with_ids = [
                            articles_collection.find_one({'filename': rec['filename']})
                            for rec in fasttext_recommendations
                        ]

                        all_scribert_recommendations.append({
                            'clicked_article': clicked_article,
                            'recommendations': scribert_recommendations_with_ids
                        })
                        all_fasttext_recommendations.append({
                            'clicked_article': clicked_article,
                            'recommendations': fasttext_recommendations_with_ids
                        })

                initial_recommendations = select_initial_recommendations()
        all_articles = list(articles_collection.find())
        random_articles = random.sample(all_articles, min(len(all_articles), 15))

    except Exception as e:
        flash(f'Makaleler yüklenirken hata oluştu: {str(e)}')
        random_articles = []

    return render_template('index.html', articles=random_articles, username=username, 
                           all_scribert_recommendations=all_scribert_recommendations, 
                           all_fasttext_recommendations=all_fasttext_recommendations, 
                           initial_recommendations=initial_recommendations)



@app.route('/article/<article_id>')
def article_detail(article_id):
    try:
        article = articles_collection.find_one({'_id': ObjectId(article_id)})
        if article:
             # Kullanıcının tıkladığı makaleyi 'clicked_articles' listesine ekleyin
            current_user.clicked_articles.append(article_id)
            filename = article.get('filename')
            users_collection.update_one(
                {'_id': current_user.id},
                {'$addToSet': {'clicked_articles': filename}}
            )
            flash('Makale kaydedildi.')
            return render_template('article_detail.html', article=article)
        else:
            flash('Makale bulunamadı.')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        interests = request.form['interests']

        if not username or not password or not age or not gender or not interests:
            flash('Lütfen tüm alanları doldurun.')
            return redirect(url_for('register'))

        interests_list = [interest.strip() for interest in interests.split(',')]
        user_data = {
            '_id': ObjectId(),
            'username': username,
            'password': password,
            'age': age,
            'gender': gender,
            'interests': interests_list
        }

        try:
            result = users_collection.insert_one(user_data)
            if result.inserted_id:
                flash('Kayıt başarılı.')
            else:
                flash('Kayıt başarısız oldu.')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            user_obj = User(user['_id'], user['username'])  # Kullanıcı nesnesi oluştur
            login_user(user_obj)  # Kullanıcıyı oturum açık olarak işaretle
            flash('Giriş başarılı.')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre yanlış.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # Oturumu sonlandır
    flash('Başarıyla çıkış yaptınız.')
    return redirect(url_for('index'))


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    # Kullanıcının veritabanındaki bilgilerini alın
    user = users_collection.find_one({'username': username})
    if not user:
        flash('Kullanıcı bulunamadı.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Profil düzenleme formundan gelen verileri işleyin
        age = request.form.get('age')
        gender = request.form.get('gender')
        interests = request.form.get('interests')
        interests_list = [interest.strip() for interest in interests.split(',')]

        # Kullanıcının verilerini güncelleyin
        users_collection.update_one({'username': username}, {'$set': {
            'age': age,
            'gender': gender,
            'interests': interests_list
        }})

        flash('Profil güncellendi.')
        return redirect(url_for('profile', username=username))

    return render_template('profile.html', user=user)





@app.route('/recommend/<username>')
def recommend(username):
    user = users_collection.find_one({'username': username})
    if user:
        interests = user['interests']
        recommendations = articles_collection.find({'keys': {'$in': interests}}).limit(10)
        return render_template('recommend.html', recommendations=recommendations, username=username)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)