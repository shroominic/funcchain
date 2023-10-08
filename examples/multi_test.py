from langchain.pydantic_v1 import BaseModel, Field
from typing import Union
from funcchain import chain


class Item(BaseModel):
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Description of the item")
    keywords: list[str] = Field(..., description="Keywords for the item")


class ShoppingList(BaseModel):
    items: Item
    store: str = Field(..., description="The store to buy the items from")


class TodoList(BaseModel):
    todos: Item
    urgency: int = Field(..., description="The urgency of all tasks (1-10)")


def gather_infos(user_input: str) -> Union[TodoList, ShoppingList]:
    """
    USER_INPUT:
    {user_input}

    The user input is either a shopping list or a todo list.
    """
    return chain()


def main():
    user_input = input("Enter your list: ")

    obj = gather_infos(user_input)

    print("Type: ", type(obj))
    print("Object: ", obj)


if __name__ == "__main__":
    main()
