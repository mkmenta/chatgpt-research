
import argparse
import json
import os
from pprint import pprint
from mongoengine import connect

from models.user import User


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help="File with username and password separated by tabs")
    return parser.parse_args()


def main(args):
    f = open(args.file, 'r')
    connect(host=os.environ.get('MONGOURI'))
    for line in f:
        username, password = line[:-1].split('\t')
        user = User.register(username=username,
                             email=None,
                             password=password)
        user.save()
        print(f"{username} registered with password: {password}")


if __name__ == '__main__':
    main(args())
