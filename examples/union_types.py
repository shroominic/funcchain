from funcchain import chain
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(description="Name of the item")
    description: str = Field(description="Description of the item")
    keywords: list[str] = Field(description="Keywords for the item")


class ShoppingList(BaseModel):
    items: list[Item]
    store: str = Field(description="The store to buy the items from")


class TodoList(BaseModel):
    todos: list[Item]
    urgency: int = Field(description="The urgency of all tasks (1-10)")


def extract_list(user_input: str) -> TodoList | ShoppingList:
    """
    The user input is either a shopping List or a todo list.
    """
    return chain()


user_input = "I need to buy apples, oranges and bananas from whole foods"
lst = extract_list(user_input)

match lst:
    case ShoppingList(items=items, store=store):
        print("Here is your Shopping List: ")
        for item in items:
            print(f"{item.name}: {item.description}")
        print(f"You need to go to: {store}")

    case TodoList(todos=todos, urgency=urgency):
        print("Here is your Todo List: ")
        for item in todos:
            print(f"{item.name}: {item.description}")
        print(f"Urgency: {urgency}")
