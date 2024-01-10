from funcchain import chain


def generate_legal_questions() -> list[str]:
    """
    Generate a full list of legal questions my client needs to answer
    so I can create the perfect Terms of Service and Privacy Policy for them.
    """
    return chain()


example_legal_questions = [
    "What is the core function of your startup?",
    "What kind of data will you be collecting from users?",
    "How do you plan to use this collected data?",
    "Will you be sharing user data with third parties?",
    "Do you plan to store payment information?",
    "What security measures are in place to protect user data?",
    "What is your data retention policy?",
    "What will be the user's rights regarding data modification or deletion?",
    "How will you handle data breaches?",
    "What is your refund or cancellation policy?",
    "Are there any age restrictions for using the service?",
    "How will you handle user complaints or disputes?",
    "Will there be any user-generated content? If yes, what are the guidelines?",
    "Do you plan to use cookies or tracking technologies?",
    "Are there any geographic restrictions or limitations?",
    "What is the procedure for updating the Terms of Service or Privacy Policy?",
    "Is your service compliant with laws like GDPR or CCPA?",
    "Will the service have a subscription model?",
    "Are there penalties for misuse of the service?",
    "Will you have any partnerships that affect the Terms of Service?",
    "Do you have a Data Protection Officer (DPO)?",
    "How will you handle data transfers outside the EU?",
    "Will you conduct Data Protection Impact Assessments (DPIAs)?",
    "How will you inform users about their 'Right to Be Forgotten'?",
    "How will you handle Subject Access Requests (SARs)?",
    "What are your protocols for gaining explicit user consent for data processing?",
]


def generate_tos(answered_questions: list[str]) -> str:
    """
    Based on the answered questions generate a Terms of Service.
    Respond with the full markdown text of the Terms of Service.
    """
    return chain()


def generate_pp(answered_questions: list[str]) -> str:
    """
    Based on the answered questions generate a Privacy Policy.
    Respond with the full markdown text of the PP.
    """
    return chain()


if __name__ == "__main__":
    print("Please answer the following questions to generate a Terms of Service and Privacy Policy.")
    print("To skip a question, press enter without typing anything.")

    legal_questions = example_legal_questions.copy()
    # or from scratch using generate_legal_questions()

    for i, question in enumerate(legal_questions):
        answer = input(f"{i+1}/{len(legal_questions)}: {question} ") or "No answer provided."

        legal_questions[i] = f"Q: {question}\nA: {answer}\n"

    tos = generate_tos(legal_questions)
    pp = generate_pp(legal_questions)

    print("Terms of Service:\n", tos)
    print("Privacy Policy:\n", pp)
