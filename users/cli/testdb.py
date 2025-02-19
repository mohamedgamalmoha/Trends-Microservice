from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


def setup_parser(subparsers):
    parser = subparsers.add_parser(
        'testdb',
        help='Test the database connection'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Database name'
    )
    parser.add_argument(
        '--user',
        required=True,
        help='Database user'
    )
    parser.add_argument(
        '--password',
        required=True,
        help='Database password'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Database host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        default='5432',
        help='Database port (default: 5432)'
    )
    parser.add_argument(
        '--engin',
        default='postgresql',
        help='Database engin (default: postgresql)'
    )
    return parser


def test_db_connection(database_url):
    engine = create_engine(
        url=database_url
    )
    try:
        with engine.connect() as connection:
            print("Database connection successful!")
            return True
    except SQLAlchemyError as e:
        print(f"Database connection failed: {str(e)}")
        return False


def handle(args):
    SQLALCHEMY_DATABASE_URL = f"{args.engin}://{args.user}:{args.password}@u{args.host}:{args.port}/{args.name}"
    test_db_connection(SQLALCHEMY_DATABASE_URL)
