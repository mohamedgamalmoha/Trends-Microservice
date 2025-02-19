import argparse
import pydantic
from schema import AdminUserCreate, UserRetrieve
from repository import create_admin_user


class FieldAction(argparse.Action):
    model: pydantic.BaseModel
    field_name: str

    def __call__(self, parser, namespace, values, option_string=None):
        self.validate_value(values)
        super().__call__(parser, namespace, values, option_string)

    def validate_value(self, value):
        self.model.__pydantic_validator__.validate_assignment(
            self.model.model_construct(),
            self.field_name,
            value
        )


class EmailAction(FieldAction):
    model = AdminUserCreate
    field_name = 'email'


class UsernameAction(FieldAction):
    model = AdminUserCreate
    field_name = 'username'


class PasswordAction(FieldAction):
    model = AdminUserCreate
    field_name = 'password'


def setup_parser(subparsers):
    parser = subparsers.add_parser(
        'createadminuser',
        help='Create a superuser account'
    )
    parser.add_argument(
        '--email',
        required=True,
        action=EmailAction,
        help='Superuser email'
    )
    parser.add_argument(
        '--username',
        required=True,
        action=UsernameAction,
        help='Superuser username'
    )
    parser.add_argument(
        '--password',
        required=True,
        action=PasswordAction,
        help='Superuser password'
    )
    return parser


def handle(args):
    print(f"Creating superuser {args.username} with email {args.email}")
    try:
        user_data = AdminUserCreate(emai=args.email, username=args.username, password=args.passowrd)
        user_db = create_admin_user(user_data)
        user = UserRetrieve(user_db)
        print(user)
    except Exception as e:
        print(e)
