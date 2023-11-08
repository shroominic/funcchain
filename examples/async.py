from funcchain import chain


def random_city() -> str:
    """
    Tell me a random city, i need this for a game.
    """
    return chain()


async def random_city_async() -> str:
    """
    Tell me a random city, i need this for a game.
    """
    return await chain()


if __name__ == "__main__":
    print(random_city())

    from asyncio import run

    print(run(random_city_async()))
