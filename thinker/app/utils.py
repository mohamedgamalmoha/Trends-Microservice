import re
from typing import Tuple


def split_think_content(text: str) -> Tuple[str, str]:
    """
    Splits the input text into two parts: the content inside the <think> tags and the remaining content.

    This function uses a regular expression to search for and capture the content enclosed within <think>...</think>
    tags, as well as the rest of the text outside those tags. It returns a tuple containing the content inside the <think> 
    tags and the content outside of them.

    Args:
        - text (str): The input string to be processed, which may contain <think> tags.

    Returns:
        - Tuple[str, str]: A tuple where:
            - The first element is the content inside the <think>...</think> tags, or an empty string if no such content is found.
            - The second element is the remaining content outside the <think> tags.
    """
    # Regex pattern to match the content inside <think> and the rest of the string
    pattern = r'(<think>.*?</think>)|([^<]*)'

    # Find all matches
    matches = re.findall(pattern, text, flags=re.DOTALL)

    # Initialize variables to hold the two parts
    think_content = ""
    remaining_content = ""

    # Extract the content from the matches
    for match in matches:
        if match[0]:  # If it's the <think> part
            think_content = match[0]
        elif match[1]:  # If it's the remaining content
            remaining_content = match[1]

    return think_content, remaining_content
