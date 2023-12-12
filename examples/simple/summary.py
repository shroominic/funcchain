from funcchain import chain


def summary(file_content: str) -> str:
    """
    Summarize the file content.
    """
    return chain()


def main() -> None:
    file_path = input("\nEnter file path: ")

    with open(file_path, "r") as f:
        file_content = f.read()

    result = summary(file_content)

    print("\nSUMMARY:\n", result)


if __name__ == "__main__":
    main()
