import random
from typing import List
from datetime import datetime

import faker
import factory


fake = faker.Faker()


class TrendsProvider(faker.providers.BaseProvider):
    SEARCH_TOPICS = [
        "python", "programming",
        "data science",
        "machine learning",
        "web development",
        "testing",
        "automation",
        "sql",
        "nosql",
        "cloud computing",
        "devops",
        "tensorflow",
        "pytorch",
        "artificial intelligence",
        "software engineering"
    ]
    PROPERTY_ENUM = [
        "web",
        "youtube",
        "news",
        "images",
        "froogle"
    ]
    DURATION = [
        "1d",
        "1w",
        "1m",
        "1y"
    ]

    def search_query(self, size: int) -> List[str]:
        return random.choices(self.SEARCH_TOPICS, k=size)

    def property_enum(self) -> str:
        return random.choice(self.PROPERTY_ENUM)

    def duration(self) -> str:
        return random.choice(self.DURATION)


fake.add_provider(TrendsProvider)


class TrendsCreateFactory(factory.Factory):
    q = factory.LazyFunction(lambda : fake.search_query(size=2))
    geo = factory.LazyFunction(lambda: fake.country_code())
    time = factory.LazyFunction(lambda: fake.duration())
    cat = factory.LazyFunction(lambda: random.randint(0, 100))
    gprop = factory.LazyFunction(lambda: fake.property_enum())
    tz = factory.LazyFunction(lambda: random.randint(-12, 12))
    schedule_at = factory.LazyFunction(datetime.now)

    class Meta:
        model = dict


class TrendsUpdateFactory(factory.Factory):
    q = factory.LazyFunction(lambda : fake.search_query(size=2))
    geo = factory.LazyFunction(lambda: fake.country_code())
    time = factory.LazyFunction(lambda: fake.duration())
    gprop = factory.LazyFunction(lambda: fake.property_enum())
    cat = factory.LazyFunction(lambda: random.randint(0, 100))
    tz = factory.LazyFunction(lambda: random.randint(-12, 12))

    class Meta:
        model = dict
