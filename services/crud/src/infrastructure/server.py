from infrastructure.configs import get_config

from .api.app import create_app
from .providers.container import create_container

config = get_config()
container = create_container()
app = create_app(container, config)
