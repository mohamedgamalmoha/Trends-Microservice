import random
import string

import faker
import factory

fake = faker.Faker()


class UserProvider(faker.providers.BaseProvider):

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


fake.add_provider(UserProvider)


class UserCreateFactory(factory.Factory):
    email = factory.Faker('email')
    username = factory.LazyFunction(lambda: fake.username(min_length=10))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.LazyFunction(lambda: fake.phonenumber(max_length=15))
    password = factory.Faker('password')
    password_confirm = factory.SelfAttribute('password')  # Match password

    class Meta:
        model = dict


class UserUpdateFactory(factory.Factory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = dict
