import os


def get_config():
    return dict(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get('SURIROBOT_DB'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
