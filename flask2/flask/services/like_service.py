from database import Session_safe
from models.post import Post
from models.user import User
from models.like import Like

class LikeService:
    @staticmethod
    def toggle_like(post_id, user_id):
        db = Session_safe()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return False, "Пост не найден"
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Пользователь не найден"
            
            existing_like = db.query(Like).filter(
                Like.post_id == post_id,
                Like.user_id == user_id,
            ).first()

            if existing_like:
                #Удаляем лайе если пользователь его уже ставил
                db.delete(existing_like)
                db.commit()
                return True, "Лайк удален"
            else:
                #Ставим лайк если до этого его не было
                new_like = Like(post_id=post_id, user_id=user_id)
                db.add(new_like)
                db.commit()
                return True, "Лайк поставлен"
        except Exception:
            db.rollback()
            return False, f"Ошибка при добавлении лайка {str(Exception)}"
        finally:
            db.close()

    @staticmethod
    def get_likes_count(post_id):
        db = Session_safe()
        try:
            count = db.query(Like).filter(Like.post_id == post_id).count()
            return count
        finally:
            db.close()

    @staticmethod
    def has_user_liked(post_id, user_id):
        db = Session_safe()
        try:
            like = db.query(Like).filter(
                Like.post_id == post_id,
                Like.user_id == user_id,
            ).first()
            return like is not None
        finally:
            db.close()