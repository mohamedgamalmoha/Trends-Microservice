from db import engine
from models import Base


def setup_parser(subparsers):
    parser = subparsers.add_parser(
        'createdb',
        help='Create the database'
    )
    return parser


def handle(args):
    Base.metadata.create_all(bind=engine)
    print('Database is created')
