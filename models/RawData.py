from datetime import datetime
from mongoengine import *
import os
from datetime import datetime

connectionString = os.environ['MONGO_URI']

connect(host=connectionString)

class RawData(Document):
    data = DictField(required=True)
    apiName = StringField(required=True, max_length=200)
    createdAt = DateTimeField(default=datetime.utcnow)