import os
from pathlib import Path
import uuid
from flask import Flask, flash, render_template, request, redirect, url_for, session
from services.user_service import UserService
from services.post_service import PostService
from services.like_service import LikeService
from services.comment_service import CommentService
from config import SECRET_KEY
from database import init_db
import re

app = Flask(__name__)
app.secret_key = SECRET_KEY


BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'posts'
AVATAR_FOLDER = BASE_DIR / 'static' / 'uploads' / 'avatars'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)  # Автоматически создает всю структуру папок
AVATAR_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['AVATAR_FOLDER'] = str(AVATAR_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024   #не больше 16 МБ
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1] in ALLOWED_EXTENSIONS 

def generate_unique_filename(filename):
    """Генерируем уникальное имя файла"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


# Или более продвинутый вариант с поддержкой абзацев:
@app.template_filter('nl2br')
def nl2br_advanced(text):
    """Преобразует \n в <br> и двойные переносы в абзацы"""
    if not text:
        return ''
    
    # Заменяем \r\n и \r на \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Разбиваем на абзацы (два переноса = новый абзац)
    paragraphs = text.split('\n\n')
    
    # Обрабатываем каждый абзац
    result = []
    for paragraph in paragraphs:
        if paragraph.strip():  # Пропускаем пустые абзацы
            # Заменяем одиночные переносы внутри абзаца на <br>
            paragraph = paragraph.replace('\n', '<br>')
            result.append(f'<p>{paragraph}</p>')
    
    return ''.join(result)


@app.route('/')
@app.route('/home')
def index():
    """Главная страница с последними постами"""
    posts = PostService.get_latest_posts(limit=5)
    return render_template('index.html', posts=posts)

@app.route('/categories')
def categories():
    flash("Раздел в разработке", "info")
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Страница поиска с формой и результатами"""
    search_query = request.args.get('q', '').strip()
    search_results = []
    
    if search_query:
        search_results = PostService.search_posts(search_query)
    
    return render_template('search.html', 
                           search_query=search_query,
                           search_results=search_results)

@app.context_processor
def inject_current_user():
    if 'user_login' in session:
        user = UserService.get_user_login(session['user_login'])
        if user:
            return dict(current_user=user)
    return dict(current_user=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        gender = request.form['gender']
        name = request.form['name']
        
        user, message = UserService.create_user(login, password, gender, name)
        if user:
            session['user_login'] = user.login
            flash(message)
            return redirect(url_for('index'))
        else:
            flash(message)
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        user = UserService.authenticate(login, password)

        if user:
            session['user_login'] = user.login
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            flash("Неверное имя пользователи или пароль")
            return render_template('login.html', error = 'Неверные данные')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_login' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    print(session['user_login'])
    user = UserService.get_user_login(session['user_login'])
    print(user)
    user = UserService.get_user_with_posts(user_id)
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('index'))
    return render_template('profile.html', user = user)



@app.route('/profile/edit', methods = ['GET', 'POST'])
def edit_profile():
    if 'user_login' not in session:
        return redirect(url_for('login'))
    user = UserService.get_user_login(session['user_login'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        errors = []
        if new_password:
            if len(new_password) < 5:
                errors.append('Пароль не должен быть короче 5 символов')
            if new_password != confirm_password:
                errors.append('Пароли не совпадают')
        if not name or len(name) < 2:
             errors.append('Имя не должно быть короче 2 символов')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('edit_profile.html', user = user)
        
        success, message = UserService.update_profile(
            id = user.id,
            name = name,
            gender=gender,
            new_password = new_password if new_password else None
        )

        if success:
            flash('Профиль успешно обновлён', 'message')
            return redirect(url_for('profile'))
        else:
            flash(message, 'error')
        
    return render_template('edit_profile.html', user = user)
        

@app.route('/user/<int:user_id>')
def view_user_profile(user_id):
    """Просмотр профиля другого пользователя"""
    user = UserService.get_user_with_posts(user_id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('index'))
    
    # Посты уже загружены в get_user_with_posts
    user_posts = user.posts if user.posts else []
    
    return render_template('user_profile.html', user=user, posts=user_posts)


    
@app.route('/pop')
def pop():
    return render_template('pop.html')

@app.route('/logout')
def logout():
    session.pop('user_login', None)
    flash("Вы вышли из системы")
    return redirect(url_for('index'))

@app.route('/posts')
def posts():
    """Страница со всеми постами"""
    all_posts = PostService.get_all_posts()
    return render_template('posts.html', posts=all_posts)

    

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_login' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = generate_unique_filename(file.filename)
                filepath = UPLOAD_FOLDER / filename
                file.save(filepath)
                image_path = os.path.join('uploads', 'posts', filename).replace('\\', '/')

        post, message = PostService.create_post(title, content, user_id, image_path)

        if post:
            return redirect(url_for('index'))
        else:
            flash(message, 'error')
            return redirect(url_for('create_post'))

    return render_template('create_post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = PostService.get_post_by_id(post_id)
    if not post:
        flash('Пост не найден', 'error')
        return redirect(url_for('index'))
    
    return render_template('post.html', post=post)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_login' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    post = PostService.get_post_by_id(post_id)
    if not post:
        flash('Пост не найден', 'error')
        return redirect(url_for('index'))
    
    # Проверка прав на редактирование
    if post.user_id != session['user_id']:
        flash('У вас нет прав на редактирование этого поста', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        updated_post, message = PostService.update_post(post_id, title, content)
        
        if updated_post:
            flash('Пост успешно обновлен!', 'success')
            return redirect(url_for('view_post', post_id=post_id))
        else:
            flash(message, 'error')
    
    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if 'user_login' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    post = PostService.get_post_by_id(post_id)
    if not post:
        flash('Пост не найден', 'error')
        return redirect(url_for('index'))
    
    # Проверка прав на удаление
    if post.user_id != session['user_id']:
        flash('У вас нет прав на удаление этого поста', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    success, message = PostService.delete_post(post_id)
    
    if success:
        flash('Пост успешно удален', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('index'))


@app.route('/post/<int:post_id>/like', methods=['POST'])
def toggle_like(post_id):
    """Добавить или удалить лайк к посту"""
    if 'user_login' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    success, message = LikeService.toggle_like(post_id, user_id)
    
    if not success:
        flash(message, 'error')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """Добавить комментарий к посту"""
    if 'user_login' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    content = request.form.get('content', '').strip()
    user_id = session.get('user_id')
    
    comment, message = CommentService.create_comment(post_id, user_id, content)
    
    if not comment:
        flash(message, 'error')
    else:
        flash('Комментарий добавлен', 'success')
    
    return redirect(request.referrer or url_for('view_post', post_id=post_id))


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    """Удалить комментарий"""
    if 'user_login' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    comment = CommentService.get_comment_by_id(comment_id)
    if not comment:
        flash('Комментарий не найден', 'error')
        return redirect(url_for('index'))
    
    post_id = comment.post_id
    user_id = session.get('user_id')
    
    success, message = CommentService.delete_comment(comment_id, user_id)
    
    if success:
        flash('Комментарий удален', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('view_post', post_id=post_id))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)