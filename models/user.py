from database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):

    id_user = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    # permission = db.Column(db.String(80), nullable=False, default="User")

    # If the name of column for different of "id", the method get_id must be overrided
    def get_id(self):
        return self.id_user
