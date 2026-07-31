from users.config import config
from monorepo.shared.broker.rabbit import create_broker

broker, app = create_broker(config.RABBIT_BROKER_URL)
