import json
import random
import re
import string
import sys
from json import JSONDecodeError

from entities import ConfigEntity, UserEntity
from network import exponential_backoff_request

API_URL = 'http://127.0.0.1:8000'
API_METHOD_SIGNUP = '/api/signup'
API_METHOD_SIGNIN = '/api/token/'
API_METHOD_CREATE_POST = '/api/posts'
API_METHOD_LIKE_POST = '/api/posts/post_id/like'


def load_config() -> ConfigEntity:
    try:
        with open('config.json') as json_file:
            data = json.load(json_file)
            return ConfigEntity(data)
    except FileNotFoundError:
        sys.exit('Missing config.json file!')
    except JSONDecodeError:
        sys.exit('Invalid config data!')
    except Exception as ex:
        sys.exit(ex)


def generate_string(size: int, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def main():
    config = load_config()
    users = []
    posts = []

    # Sign up users
    for a in range(config.number_of_users):
        user = UserEntity(generate_string(32), generate_string(8))
        response = exponential_backoff_request('POST', API_URL + API_METHOD_SIGNUP,
                                               data={
                                                   'username': user.username,
                                                   'password': user.password
                                               })
        if response.status_code == 201:
            users.append(user)
        else:
            print('Signup error')
            sys.exit(json.loads(response.text))

    # Sign in users
    for user in users:
        response = exponential_backoff_request('POST', API_URL + API_METHOD_SIGNIN,
                                               data={
                                                   'username': user.username,
                                                   'password': user.password
                                               })

        if response.status_code == 200:
            data = json.loads(response.text)
            user.access_token = data['access']
            user.refresh_token = data['refresh']
        else:
            print('Signin error')
            sys.exit(json.loads(response.text))

    # Create posts
    for user in users:
        for a in range(random.randint(1, config.max_posts_per_user)):
            response = exponential_backoff_request('POST', API_URL + API_METHOD_CREATE_POST,
                                                   headers={
                                                       'Authorization': 'Bearer ' + user.access_token,
                                                   },
                                                   data={
                                                       'text': generate_string(128)
                                                   })
            if response.status_code == 201:
                data = json.loads(response.text)
                posts.append(data['id'])
            else:
                print('Create post error')
                sys.exit(json.loads(response.text))

    # Like posts
    for user in users:
        for a in range(random.randint(1, config.max_likes_per_user)):
            response = exponential_backoff_request('POST', API_URL + re.sub(r'post_id', str(random.choice(posts)),
                                                                            API_METHOD_LIKE_POST),
                                                   headers={
                                                       'Authorization': 'Bearer ' + user.access_token,
                                                   })
            if response.status_code == 200:
                data = json.loads(response.text)
                posts.append(data['id'])
            else:
                print('Like post error')
                sys.exit(json.loads(response.text))


if __name__ == "__main__":
    main()
