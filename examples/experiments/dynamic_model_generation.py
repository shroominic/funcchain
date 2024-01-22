from funcchain import chain, settings
from funcchain.syntax.output_types import CodeBlock
from langchain_community.document_loaders import WebBaseLoader
from pydantic import BaseModel
from rich import print

settings.llm = "gpt-4-1106-preview"
settings.context_lenght = 4096 * 8


def create_model(web_page: str) -> CodeBlock:
    """
    Based on the pure web page, create a Pydantic to extract the core contents of the page.
    Create now a Pydantic model to represent this structure.
    Only include imports and the model class.
    Always name the class "StructuredOutput". The user can change it later.
    """
    return chain()


def fix_imports(error: str) -> CodeBlock:
    """
    Write proper import statements for the given error.
    """
    return chain()


if __name__ == "__main__":
    url = input("Give me a link and I scrape your page!\n> Url: ")

    page = WebBaseLoader(url).load()

    model = create_model(page.__str__())

    print("Model:\n", model.code)

    try:
        exec(model.code)
    except Exception as e:
        imports = fix_imports(str(e))
        exec(imports.code)
        exec(model.code)

    class StructuredOutput(BaseModel):
        ...

    def scrape_page(
        page: str,
    ) -> StructuredOutput:
        """
        Scrape the unstructured data into the given shape.
        """
        return chain()

    output = scrape_page(str(page))

    print(output)
