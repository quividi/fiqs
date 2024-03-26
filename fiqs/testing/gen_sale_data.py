import json
import random

from fiqs.testing.gen_data import (
    random_shop_id,
    random_string,
    random_timestamp,
)

PRODUCT_TYPES = [f"product_type_{i}" for i in range(5)]
PRODUCT_IDS = [f"product_{random_string(10)}" for _ in range(50)]
PRODUCTS = [(product_id, random.choice(PRODUCT_TYPES)) for product_id in PRODUCT_IDS]


def gen_parts(product_price):
    parts = []
    nb_parts = random.randint(1, 10)

    for _ in range(nb_parts):
        parts.append(
            {
                "part_id": f"part_{random.randint(1, 10)}",
                "warehouse_id": f"warehouse_{random.randint(1, 10)}",
                "part_price": int(product_price / (nb_parts * 1.5)),
            }
        )

    return parts


def gen_products(price):
    products = []
    nb_products = random.randint(1, 5)

    for i in range(nb_products):
        if i == nb_products - 1:
            product_price = price - sum(p["product_price"] for p in products)
        else:
            product_price = price / 10

        product_id, product_type = random.choice(PRODUCTS)

        products.append(
            {
                "product_id": product_id,
                "product_type": product_type,
                "product_price": product_price,
                "parts": gen_parts(product_price),
            }
        )

    return products


def gen_shop_data(size):
    for i in range(size):
        price = random.randint(10, 1000)
        print(
            json.dumps(
                {
                    "id": i + 1,
                    "shop_id": random_shop_id(),
                    "client_id": f"client_{random_string(10)}",
                    "timestamp": random_timestamp(),
                    "price": price,
                    "payment_type": random.choice(
                        [
                            "wire_transfer",
                            "cash",
                            "store_credit",
                        ]
                    ),
                    "products": gen_products(price),
                }
            )
        )


if __name__ == "__main__":
    size = 500
    gen_shop_data(size)
