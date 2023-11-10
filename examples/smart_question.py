from funcchain import Matrix, achain  # type: ignore

# Matrix is a type annotation that tells the backend
# to run n versions of this prompt in parallel and
# summarizes the results.
# This corrects for any errors in the model and improves
# the quality of the answer.


# NOT YET WORKING (TODO)
async def generate_answer(question: Matrix[str], context: list[str] = []) -> str:
    """
    Generate an answer to the question based on the context.
    If no context is provided just use the question.
    """
    return await achain()
