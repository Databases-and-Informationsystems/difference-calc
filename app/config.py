import os


class Config:
    DEBUG = (
        os.getenv("DEBUG", "False") == "1"
        or os.getenv("DEBUG", "True").lower() == "true"
    )
