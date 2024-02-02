from funcchain import BaseModel, Error, chain
from rich import print


class User(BaseModel):
    name: str
    email: str | None


def extract_user_info(text: str) -> User | Error:
    """
    Extract the user information from the given text.
    In case you do not have enough infos, raise.
    """
    return chain()


if __name__ == "__main__":
    print(extract_user_info("hey"))  # returns Error

    print(extract_user_info("I'm John and my mail is john@gmail.com"))  # returns a User object
