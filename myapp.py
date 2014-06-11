import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class MyDatabaseConnector(object):
    engine = None
    Session = None
    connection = None

    def __init__(self):
        self.connect()

    def connect(self):
        if self.engine is None:
            self.engine = create_engine(os.getenv('LOCAL_DB_URL'), echo=False, pool_size=100, pool_recycle=499,
                                        pool_timeout=20)

            if self.Session is None:
                self.Session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))
                self.Session.configure( bind=self.engine)

            if self.connection is None:
                self.connection = self.engine.connect()


    def get_session(self):
        self.connect()
        return self.Session


    def close(self):
        self.Session.remove()


db_connector = MyDatabaseConnector()


def create_app():
    app = Flask(__name__)
    return app