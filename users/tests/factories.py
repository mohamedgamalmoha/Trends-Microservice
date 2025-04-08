import random
import string
from typing import Any, Dict
from datetime import datetime
from functools import partial

import faker
import factory

from app.models.user import User


fake = faker.Faker()


class CustomProvider(faker.providers.BaseProvider):

    def username(self, min_length=10):
        # Generate a random username
        username = self.generator.user_name()
        # Ensure the username is at least 10 characters long
        while len(username) < min_length:
            # Add random characters if the username is too short
            username += random.choice(string.ascii_lowercase + string.digits)
        return username
    
    def phonenumber(self, max_length=15):
        # Generate a random phone number
        phone_number = self.generator.phone_number()
        
        # Ensure the phone number doesn't exceed the max_length
        while len(phone_number) > max_length:
            # Trim the phone number if it's too long
            phone_number = phone_number[:-1]
        # Add random digits if the phone number is too short
        return phone_number


fake.add_provider(CustomProvider)


class UserFactory(factory.Factory):
    id = factory.Sequence(lambda n: n)
    email = factory.Faker('email')
    username = factory.LazyFunction(lambda: fake.username(min_length=10))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.LazyFunction(lambda: fake.phonenumber(max_length=15))
    password = factory.Faker('password')
    is_admin = False
    is_active = True
    date_created = factory.LazyFunction(datetime.now)
       
    class Meta:
        model = User


class UserCreateFactory(factory.Factory):
    email = factory.Faker('email')
    username = factory.LazyFunction(lambda: fake.username(min_length=10))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.LazyFunction(lambda: fake.phonenumber(max_length=15))
    password = factory.Faker('password')
    password_confirm = factory.SelfAttribute('password')  # Match password

    class Meta:
        model = User


def generate_dict_factory(factory_cls: factory.Factory):

    def convert_dict_from_stub(stub: factory.base.StubObject) -> Dict[str, Any]:
        stub_dict = stub.__dict__
        for key, value in stub_dict.items():
            if isinstance(value, factory.base.StubObject):
                stub_dict[key] = convert_dict_from_stub(value)
        return stub_dict

    def dict_factory(factory_cls, **kwargs):
        stub = factory_cls.stub(**kwargs)
        stub_dict = convert_dict_from_stub(stub)
        return stub_dict

    return partial(dict_factory, factory_cls)


UserCreateFactoryDict = generate_dict_factory(UserCreateFactory)
UserFactoryDict = generate_dict_factory(UserFactory)
