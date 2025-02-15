from fastapi import FastAPI

import models
from db import engine


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


from routes import *
