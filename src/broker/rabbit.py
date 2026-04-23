from faststream.rabbit import RabbitBroker

from core.utils import get_broker_url

broker = RabbitBroker(get_broker_url())
