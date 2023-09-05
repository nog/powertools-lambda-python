from dataclasses import dataclass

from aws_lambda_powertools.utilities.idempotency import (
    DynamoDBPersistenceLayer,
    IdempotencyConfig,
    idempotent_function,
)
from aws_lambda_powertools.utilities.idempotency.serialization.dataclass import DataclassSerializer
from aws_lambda_powertools.utilities.typing import LambdaContext

dynamodb = DynamoDBPersistenceLayer(table_name="IdempotencyTable")
config = IdempotencyConfig(event_key_jmespath="order_id")  # see Choosing a payload subset section


@dataclass
class OrderItem:
    sku: str
    description: str


@dataclass
class Order:
    item: OrderItem
    order_id: int


@dataclass
class OrderOutput:
    order_id: int


@idempotent_function(
    data_keyword_argument="order",
    config=config,
    persistence_store=dynamodb,
    output_serializer=DataclassSerializer,
)
# order output is deduced from return type
def deduced_order_output_serializer(order: Order) -> OrderOutput:
    return OrderOutput(order_id=order.order_id)


def lambda_handler(event: dict, context: LambdaContext):
    config.register_lambda_context(context)  # see Lambda timeouts section
    order_item = OrderItem(sku="fake", description="sample")
    order = Order(item=order_item, order_id=1)

    # `order` parameter must be called as a keyword argument to work
    deduced_order_output_serializer(order=order)
