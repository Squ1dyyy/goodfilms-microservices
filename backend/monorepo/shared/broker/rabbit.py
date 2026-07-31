from faststream import FastStream
from faststream.rabbit import RabbitBroker


def create_broker(broker_url: str) -> tuple[RabbitBroker, FastStream]:
    broker = RabbitBroker(broker_url)
    app = FastStream(broker)
    return broker, app
