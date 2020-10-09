import sys


class ConfigEntity:
    number_of_users: int
    max_posts_per_user: int
    max_likes_per_user: int

    def __init__(self, data: dict):
        try:
            self.number_of_users = data['number_of_users']
            self.max_posts_per_user = data['max_posts_per_user']
            self.max_likes_per_user = data['max_likes_per_user']
        except KeyError as ex:
            sys.exit('Invalid config data! Missing %s parameter.' % ex)
        except Exception as ex:
            sys.exit(ex)


class UserEntity:
    username: str
    password: str
    access_token: str
    refresh_token: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

