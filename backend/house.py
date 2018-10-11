from .user import User
from .device import Device


class House():
    def __init__(self, house_id):
        self.id = house_id
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def remove_user(self, user_id):
        for user in self.users:
            if (user.get_id() == user_id):
                self.users.remove(user)

    def get_user(self, user_id):
        for user in self.users:
            if (user.get_id() == user_id):
                return user
