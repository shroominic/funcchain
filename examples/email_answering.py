import subprocess
from typing import List, Tuple

from funcchain import chain


def get_emails_from_inbox() -> List[Tuple[str, str]]:
    email_list = []

    # AppleScript to get email titles and contents from Mail app
    apple_script = """
    set output to ""
    tell application "Mail"
        set theMessages to every message of inbox
        repeat with aMessage in theMessages
            set output to output & subject of aMessage & ":::::" & content of aMessage & "|||||"
        end repeat
    end tell
    return output
    """

    # Run AppleScript and collect output
    process = subprocess.Popen(["osascript", "-e", apple_script], stdout=subprocess.PIPE)
    out, _ = process.communicate()
    raw_output = out.decode("utf-8").strip()

    # Parse the output into a list of (email_title, email_content) tuples
    for email_data in raw_output.split("|||||"):
        if email_data:
            title, content = email_data.split(":::::")
            email_list.append((title, content))

    return email_list


# example usage
emails = get_emails_from_inbox()
print(emails[0])


personal_context = """
I am an AI Engineer working on my own projects and doing some freelancing.
My name is Dominic Bäumer and I am 20 years old.
I live in Germany and I just quit studying artificial intelligence.
"""


def answer_email(email: str, personal_context: str) -> str:
    """
    EMAIL:
    {email}

    PERSONAL_CONTEXT:
    {personal_context}

    Answer the email using the personal context.
    """
    return chain()


for email in emails:
    print("\nEmailTitle:\n", email[0])
    print("\nEmailContent:\n", email[1])
    print("\nAnswer: \n", answer_email(email[1], personal_context))
    print("-----")
