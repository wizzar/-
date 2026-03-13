from datetime import datetime
from .base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable = False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", backref="comments")
    author = relationship("User", backref="comments")

    def __repr__(self):
        return f'Comment post_id={self.post_id} user_id={self.user_id}'