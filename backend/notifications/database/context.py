from notifications.config import config
import notifications.core.redis_config as redis_cfg
from monorepo.shared.db.session import make_session_factory, make_get_db
from monorepo.shared.cache.dependency import make_get_redis

engine, AsyncSessionLocal = make_session_factory(config.DATABASE_URL)

get_db = make_get_db(AsyncSessionLocal)
get_redis = make_get_redis(redis_cfg)
