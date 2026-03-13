from models.user import User
from database import Session_safe
from models.post import Post
from models.like import Like
from models.comment import Comment

class UserService:

    @staticmethod
    def create_user(login, password, gender, name):
        db = Session_safe()
        if db.query(User).filter(User.login == login).first():
            return None, "Пользователь с таким логином уже существует"

        new_user = User(login, password, gender, name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user, "Пользователь успешно создан"
    
    @staticmethod
    def authenticate(login, password):
        db = Session_safe()
        if db.query(User).filter(User.login == login, User.password == password).first():
            user = db.query(User).filter(User.login == login, User.password == password).first()
            db.close()
            return user
        return None
    
    @staticmethod
    def get_user_id(id):
        db = Session_safe()
        user = db.query(User).get(id)
        db.close()
        return user

    @staticmethod
    def get_user_login(login):
        db = Session_safe()
        user = db.query(User).filter(User.login == login).first()
        db.close()
        return user
    

    @staticmethod
    def update_profile(id, name, gender, new_password = None):
        db = Session_safe()
        user = db.query(User).get(id)
        if not user:
            return False, 'Пользователь не найден'
        
        user.name = name
        user.gender = gender
        if new_password:
            user.password = new_password

        try:
            db.commit()
            return True, "Пользователь обновлён"
        except:
            db.rollback()
            return False, "Пользователь не обновлён"
        finally:
            db.close()

    @staticmethod
    def get_user_with_posts(user_id):
        db = Session_safe()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()
            
            for post in posts:
                post.likes = db.query(Like).filter(Like.post_id == post.id).all()
                
                post.comments = db.query(Comment).filter(Comment.post_id == post.id).order_by(Comment.created_at.desc()).all()
                
                for comment in post.comments:
                    comment.author = db.query(User).filter(User.id == comment.user_id).first()
            
            user.posts = posts
            
            return user
        finally:
            db.close()



