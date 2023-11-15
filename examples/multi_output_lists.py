from typing import List, Union

from pydantic.v1 import BaseModel, Field

from funcchain import chain


class Item(BaseModel):
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Description of the item")
    keywords: List[str] = Field(..., description="Keywords for the item")


class ShoppingList(BaseModel):
    """List of items to buy"""

    items: List[Item]
    store: str = Field(..., description="The store to buy the items from")


class TodoList(BaseModel):
    todos: List[Item]
    urgency: int = Field(..., description="The urgency of all tasks (1-10)")


def extract_list(user_input: str) -> Union[TodoList, ShoppingList]:
    """
    The user input is either a shopping List or a todo list.
    """
    return chain()


user_input = input("Enter your list: ")
lst = extract_list(user_input)

if isinstance(lst, ShoppingList):
    print("Here is your Shopping List: ")
    for item in lst.items:
        print(f"{item.name}: {item.description}")
    print(f"You need to go to: {lst.store}")

elif isinstance(lst, TodoList):
    print("Here is your Todo List: ")
    for item in lst.todos:
        print(f"{item.name}: {item.description}")
    print(f"Urgency: {lst.urgency}")
