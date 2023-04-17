
import argparse
import json
import os
from pprint import pprint
from mongoengine import connect

from models.user import User


def gen_password(length=16):
    import string
    import random
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str)
    parser.add_argument('--email', type=str, default=None)
    parser.add_argument('--password', type=str, default=None)
    parser.add_argument('--gen-password', action='store_true')
    parser.add_argument('--make-admin', action='store_true')
    parser.add_argument('--edit', action='store_true')
    parser.add_argument('--list', action='store_true')
    return parser.parse_args()


def main(args):
    if args.gen_password and args.password is None:
        args.password = gen_password()
        print(f"Password: {args.password}\n")
    connect(host=os.environ.get('MONGOURI'))
    if args.list:
        for user in User.objects:
            print(user.username)
    elif args.edit:
        assert args.username is not None
        assert args.email is not None or args.password is not None or args.make_admin
        user = User.objects.get(username=args.username)
        if args.email is not None:
            user.email = args.email
        if args.password is not None:
            user.update_password(args.password)
        if args.make_admin:
            user.admin = True
        pprint(json.loads(user.to_json()))
    else:
        assert args.username is not None
        assert args.email is not None
        assert args.password is not None
        user = User.register(username=args.username,
                             email=args.email,
                             password=args.password)
        user.admin = args.make_admin
        user.save()
        pprint(json.loads(user.to_json()))


if __name__ == '__main__':
    main(args())
