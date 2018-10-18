import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from backend.user import User


class House():
    def __init__(self, house_id):
        self.id = house_id
        self.users = []

    def get_id(self):
        return self.id

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user):
        self.users.remove(user)

    def get_user(self, user_id):
        for user in self.users:
            if (user.get_id() == user_id):
                return user

    def __str__(self):
        return str(self.id)
