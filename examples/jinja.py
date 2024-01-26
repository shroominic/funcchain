from funcchain import chain, settings
from pydantic import BaseModel

settings.console_stream = True


class Cart(BaseModel):
    items: list[str]
    price: float


def shopping_analysis(cart: Cart, f_instructions: bool) -> str:
    """
    Shopping List:
    {% for item in cart.items %} - {{ item }}
    {% endfor %}

    Determine if the cart is healthy or not and if the price is good.
    {% if f_instructions %} format the output as json! {% endif %}
    """
    return chain()


example_cart = Cart(
    items=["apple", "banana", "orange", "mango", "pineapple"],
    price=2.99,
)

print(shopping_analysis(example_cart, True))
print(shopping_analysis(example_cart, False))
