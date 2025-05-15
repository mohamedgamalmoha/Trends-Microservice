import random
from datetime import datetime

import faker
import factory


fake = faker.Faker()


class ThinkerCreateFactory(factory.Factory):
    question = factory.LazyFunction(lambda: fake.sentence(nb_words=10, variable_nb_words=True))
    context = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=5, variable_nb_sentences=True))
    temperature = factory.LazyFunction(lambda: round(random.uniform(0.1, 1.0), 1))
    max_tokens = factory.LazyFunction(lambda: random.choice([100, 150, 200, 250, 300, 500]))
    schedule_at = factory.LazyFunction(datetime.now)

    class Meta:
        model = dict


class ThinkerUpdateFactory(ThinkerCreateFactory):
    ...
