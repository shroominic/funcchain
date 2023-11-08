from funcchain import BaseModel, Error, chain


class User(BaseModel):
    name: str
    email: str | None


def extract_user_info(text: str) -> User | Error:
    """
    Extract the user information from the given text.
    If you do not have enough infos, raise.
    """
    return chain()


if __name__ == "__main__":
    print(extract_user_info("hello"))  # returns Error

    print(extract_user_info("My name is John at gmail.com"))  # return User
