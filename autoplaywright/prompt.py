from typing import Optional, Type
from bs4 import BeautifulSoup

from autoplaywright.types import PydanticModel


def prepare_init_prompt():
    """
    Prepare the initial system prompt for the AI model.

    This function returns a detailed instruction string that establishes the context
    and guidelines for the AI model. It explains how to analyze HTML and provides
    a comprehensive list of available Playwright actions that can be used.

    Returns:
        str: A structured prompt containing instructions and available Playwright actions
    """
    return """
    You will soon be asked to analyze HTML code and determine the appropriate actions to take.  
    Your task is to identify specific elements within the HTML and present them in the correct format or specify the necessary actions.  

    The actions provided are used to control the Playwright library in Python.  
    When constructing CSS query selectors, ensure they are unique and precise enough to target a single element, even if multiple elements of the same type exist (e.g., multiple `<h1>` elements).  
    Avoid using generic tags like `'h1'` alone. Instead, combine them with attributes or structural relationships to create a unique selector.  
    The most reliable query selectors should include an `id` or `class` attribute whenever possible, as it provides the highest level of accuracy.  
    Most reliable format: <tag>[attribute='value']

    Available actions:  
    - `add_init_script(script: str)`  
    - `bring_to_front()`  
    - `click(querySelector: str)`  
    - `close()`  
    - `dblclick(querySelector: str)`  
    - `dispatch_event(querySelector: str, type: str, eventInit: dict = None)`  
    - `evaluate(expression: str, arg: Any = None)`  
    - `fill(querySelector: str, value: str)`  
    - `focus(querySelector: str)`  
    - `go_back()`  
    - `go_forward()`  
    - `goto(url: str, options: dict = None)`  
    - `hover(querySelector: str)`  
    - `press(querySelector: str, key: str)`  
    - `reload()`  
    - `screenshot(options: dict = None)`  
    - `set_content(html: str)`  
    - `set_viewport_size(width: int, height: int)`  
    - `tap(querySelector: str)`  
    - `type(querySelector: str, text: str, options: dict = None)`  
    - `uncheck(querySelector: str)`  
    - `wait_for_event(event: str, options: dict = None)`  
    - `wait_for_load_state(state: str = 'load', options: dict = None)`  
    - `wait_for_selector(querySelector: str, options: dict = None)`  
    - `wait_for_timeout(timeout: float)`  
    - `wait_for_url(url: str, options: dict = None)`  
    """


def prepare_auto_prompt(prompt: str, html: str, output_format: Optional[Type[PydanticModel]] = None):
    """
    Prepare a prompt for the AI model containing the user's task, HTML content, and output format.

    This function processes the HTML using BeautifulSoup to clean it up, converts the Pydantic
    model to a JSON schema if provided, and constructs a detailed prompt for the AI model.

    Args:
        prompt: User's natural language instruction or task description
        html: HTML content of the current page to be analyzed
        output_format: Optional Pydantic model class specifying the required output structure

    Returns:
        str: A structured prompt containing the task, HTML content, and output format requirements

    Notes:
        - The function removes script, style, meta, title, and link tags from the HTML
          to focus on the visible content and reduce token usage
        - If a Pydantic model is provided, it will be converted to a JSON schema and included
          in the prompt to guide the output format
    """
    output_format = output_format.model_json_schema() if output_format else []

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["style", "meta", "script", "title", "link"]):
        tag.decompose()

    return f"""
    Webpage snapshot:
    ```html
    {str(soup)}
    ```

    Task assigned by the user:  
    {prompt}  
    Follow the previously provided guidelines.

    Analysis of the provided model:  
    The user has supplied a Pydantic model schema in JSON format. Analyze the model and generate a JSON output that conforms to this schema.  
    Pydantic model schema: {output_format}  

    Important guidelines:  
    - The `"outputData"` key is reserved for the extracted content based on the user's request.  
    - Replace placeholder values with actual data.  
    - If a field is not required, set it to `None`.  
    - If no actions are needed, leave the `"actions"` array empty.  

    Example output format:  
    ```json
    {{"outputData": "<replace with data>", "actions": [{{"name": "click", "args": ["input[id='searchbox_input']"]}}]}}
    ```

    Additional requirements:  
    - Use double quotes (`""`) instead of single quotes (`''`) in JSON.  
    - Return **only JSON** in your response, without any extra text.  
    """
