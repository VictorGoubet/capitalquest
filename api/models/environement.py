from enum import Enum


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
