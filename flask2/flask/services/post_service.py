from database import Session_safe
from models.post import Post
from models.user import User
from models.comment import Comment
from sqlalchemy.orm import joinedload


class PostService:
    @staticmethod
    def create_post(title, content, user_id, image_path = None):
        db = Session_safe()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None, "Пользователь не найден"
            
            if len(title) < 5:
                return None, "Заголовок должен быть не менее 5 символов"
            if len(content) < 50:
                return None, "Содержание должно быть не менее 50 символов"
            
            new_post = Post(title=title, content=content.strip(), user_id=user_id, image_path = image_path)
            
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            
            return new_post, "Пост успешно создан!"
        except Exception as e:
            db.rollback()
            return None, f"Ошибка создания поста: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_latest_posts(limit=5):
        db = Session_safe()
        try:
            posts = db.query(Post)\
                .options(joinedload(Post.author))\
                .order_by(Post.created_at.desc())\
                .limit(limit)\
                .all()
            return posts
        except Exception as e:
            print(f"Ошибка при получении постов: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_post_by_id(post_id):
        db = Session_safe()
        try:
            post = db.query(Post).options(joinedload(Post.author), joinedload(Post.likes), joinedload(Post.comments).joinedload(Comment.author)).filter(Post.id == post_id).first()
            return post
        except Exception as e:
            print(f"Ошибка при получении поста: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def update_post(post_id, title, content):
        db = Session_safe()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return None, "Пост не найден"
            
            post.title = title
            post.content = content
            db.commit()
            db.refresh(post)
            return post, "Пост успешно обновлен"
        except Exception as e:
            db.rollback()
            return None, f"Ошибка при обновлении поста: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def delete_post(post_id):
        db = Session_safe()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return False, "Пост не найден"
            
            db.delete(post)
            db.commit()
            return True, "Пост успешно удален"
        except Exception as e:
            db.rollback()
            return False, f"Ошибка при удалении поста: {str(e)}"
        finally:
            db.close()


    @staticmethod
    def get_user_posts(user_id):
        db = Session_safe()
        try:
            posts = db.query(Post)\
                .options(joinedload(Post.author))\
                .filter(Post.user_id == user_id)\
                .order_by(Post.created_at.desc())\
                .all()
            return posts
        except Exception as e:
            print(f"Ошибка при получении постов пользователя: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_all_posts():
        db = Session_safe()
        try:
            return db.query(Post).options(joinedload(Post.author)).order_by(Post.created_at.desc()).all()
        finally:
            db.close()
    