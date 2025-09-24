from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")
    followers: Mapped[list["Follower"]] = relationship("Follower", foreign_keys="Follower.followed_id", back_populates="followed")
    following: Mapped[list["Follower"]] = relationship("Follower", foreign_keys="Follower.follower_id", back_populates="follower")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat()
            # do not serialize the password, its a security breach
        }
    
class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "caption": self.caption,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "user": self.user.serialize() if self.user else None,
            "likes_count": len(self.likes),
            "comments_count": len(self.comments)
        }

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "post_id": self.post_id,
            "user": self.user.serialize() if self.user else None
        }
    
class Like(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")

    def serialize(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "post_id": self.post_id,
            "user": self.user.serialize() if self.user else None
        }
    
class Follower(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id], back_populates="followers")

    def serialize(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
            "follower": self.follower.serialize() if self.follower else None,
            "followed": self.followed.serialize() if self.followed else None
        }