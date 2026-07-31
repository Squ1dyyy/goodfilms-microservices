from faststream.rabbit import RabbitBroker
from recomendations.config import config

broker = RabbitBroker(config.RABBIT_BROKER_URL)
