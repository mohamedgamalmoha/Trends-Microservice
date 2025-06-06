import factory


class UserUpdateFactory(factory.Factory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = dict
