from datetime import datetime

from database import db


def format_datetime(date_time):
    return datetime.strptime(date_time, "%d-%m-%Y %H:%M")


class Meal(db.Model):

    id_meal = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(80))
    datetime = db.Column(db.DateTime, nullable=False)
    diet = db.Column(db.Boolean, nullable=False)

    # foreign key from class model user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)

    def get_id(self):
        return self.id_meal

    def to_dict(self):
        return {
            "id_meal": self.id_meal,
            "name": self.name,
            "description": self.description,
            "date_time": self.datetime,
            "diet": self.diet
        }

