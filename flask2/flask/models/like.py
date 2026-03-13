from datetime import datetime
from .base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", backref="likes")
    user = relationship("User", backref="likes")

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name = 'unique_post_user'),)

    def __repr__(self):
        return f'Like post_id={self.post_id} user_id={self.user_id}'
