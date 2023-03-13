import sqlalchemy

from flask_login import UserMixin
import data.db_session as db_session
from .db_session import SqlAlchemyBase


class UsersMusic(SqlAlchemyBase, UserMixin):
    __tablename__ = "usersmusic"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # autoincrement - автозаполение\
    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    music_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    music_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    music_cover = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    music_duration = sqlalchemy.Column(sqlalchemy.String, nullable=True)
