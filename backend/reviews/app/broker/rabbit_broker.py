from monorepo.shared.broker.rabbit import create_broker
from reviews.config import config

broker, app = create_broker(config.RABBIT_BROKER_URL)
