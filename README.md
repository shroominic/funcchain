# funcchain

🔖 write langchain prompts as python functions

## Demo

```python
from langchain.pydantic_v1 import BaseModel, Field
from typing import Union, List
from funchain import chain

class Item(BaseModel):
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Description of the item")
    keywords: List[str] = Field(..., description="Keywords for the item")

class ShoppingList(BaseModel):
    """ List of items to buy """
    items: List[Item]
    store: str = Field(..., description="The store to buy the items from")

class TodoList(BaseModel):
    todos: List[Item]
    urgency: int = Field(..., description="The urgency of all tasks (1-10)")

def gather_infos(user_input: str) -> Union[TodoList, ShoppingList]:
    """
    USER_INPUT:
    {user_input}

    The user input is either a shopping List or a todo list.
    """
    return chain()

def main():
    user_input = input("Enter your list: ")
    obj = gather_infos(user_input)

    if isinstance(obj, ShoppingList):
        print(obj.store)

    print("Type: ", type(obj))
    print("Object: ", obj)

if __name__ == "__main__":
    main()
```
