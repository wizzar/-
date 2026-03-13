from database import Session_safe
from models.post import Post
from models.user import User
from models.like import Like
from models.comment import Comment
from sqlalchemy.orm import joinedload

class CommentService:

    @staticmethod
    def create_comment(post_id, user_id, content):
        db = Session_safe()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return False, "Пост не найден"
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Пользователь не найден"
            
            if not content or len(content.strip()) < 1:
                return False, "Комментарий не должен быть пустым"
            if len(content) > 150:
                return False, "Комментарий не должен быть длиннее 150 символов"
            
            new_comment = Comment(content=content.strip(), post_id=post_id, user_id=user_id)
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)

            return True, "Комментари добавлен"
        except Exception:
            db.rollback()
            return False, "Ошибка при создании комментария"
        finally:
            db.close()

    @staticmethod
    def get_post_comments(post_id):
        db = Session_safe()
        try:
            comments = db.query(Comment)\
            .options(joinedload(Comment.author))\
            .filter(Comment.post_id == post_id)\
            .order_by(Comment.create_at.desc())\
            .all()
            return comments
        except Exception:
            print("Ошибка при получении комментариев")
        finally:
            db.close()

    @staticmethod
    def delete_comment(comment_id, user_id):
        db = Session_safe()
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return False, "Комментарий не найден"
            if comment.user_id != user_id:
                return False, "У вас нет прав на удаление этого комментария"
            db.delete(comment)
            db.commit()
            return True, "Комментарий удален"
        except Exception:
            db.rollback()
            return False, "Ошибка при удалении комментария"
        finally:
            db.close()

    @staticmethod
    def get_comment_by_id(comment_id):
        db = Session_safe()
        try:
           comment = db.query(Comment).options(joinedload(Comment.author)).filter(Comment.id == comment_id).first()
           return comment
        finally:
            db.close() 


    @staticmethod
    def update_comment(comment_id, user_id, new_content):
        db = Session_safe()
        try:
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            if not comment:
                return None, "Комментарий не найден"
            
            if comment.user_id != user_id:
                return None, "У вас нет прав на редактирование этого комментария"
            
            if not new_content or len(new_content.strip()) < 1:
                return None, "Комментарий не может быть пустым"
            
            if len(new_content) > 1000:
                return None, "Комментарий не должен быть длиннее 1000 символов"
            
            comment.content = new_content.strip()
            db.commit()
            db.refresh(comment)
            
            return comment, "Комментарий успешно обновлен"
        
        except Exception as e:
            db.rollback()
            return None, f"Ошибка при обновлении комментария: {str(e)}"
        finally:
            db.close()

            