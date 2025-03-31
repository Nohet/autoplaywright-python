# 🚀 Auto Playwright Python

Automating Playwright steps using ChatGPT(OpenAI) or DeepSeek in Python
<br>This library is inspired by Luc Gagan's [auto-playwright](https://github.com/lucgagan/auto-playwright) node.js library.

## Setup

Install the library using pip:

```bash
pip install autoplaywright-python
```

## Supported Browsers

Autoplaywright supports all browsers supported by Playwright, including:

- Chromium
- Firefox
- WebKit

## Usage

Below are examples demonstrating how to use the library:

### ▶️ Async Example

```python
import asyncio
from playwright.async_api import async_playwright
from pydantic import BaseModel
from autoplaywright.async_api.openai_client import AutoPlaywrightOpenAI

# Create an instance of the AI client using the GPT-4o-mini model
# Remember to replace 'OPENAI_API_KEY_HERE' with you your actual openai api key
ai = AutoPlaywrightOpenAI(model="gpt-4o-mini", api_key="OPENAI_API_KEY_HERE")


# Define a Pydantic model to store the price of the plan
class Plan(BaseModel):
    price: float


# The main function that performs the sequence of operations in the browser
async def main():
    # Launch Playwright in an asynchronous context
    async with async_playwright() as playwright:
        chromium = playwright.chromium

        # Launch the Chromium browser in non-headless mode (i.e., the browser UI is visible)
        browser = await chromium.launch(headless=False)
        page = await browser.new_page()

        # Open the test e-commerce website
        await page.goto("https://webscraper.io/test-sites/e-commerce/allinone")

        # Click the "Pricing" link in the header of the page using the AI command
        # The AI model performs the task "Click on pricing" on the page
        await ai.auto("Click on pricing", page)

        # Select the most expensive plan and return its price as a Pydantic model (Plan)
        # The AI model analyzes the page and extracts the relevant price
        plan = await ai.auto("Return price of most expensive plan", page, Plan)

        # Print the price of the most expensive plan to the console
        print(plan.price)

        # Close the page
        await page.close()


# Run the main function asynchronously
asyncio.run(main())

```

### ▶️ Sync Example

```python
from typing import List

from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from autoplaywright.sync_api.openai_client import AutoPlaywrightOpenAI


# Create an instance of the AI client using the GPT-4o-mini model
# Remember to replace 'OPENAI_API_KEY_HERE' with you your actual openai api key
ai = AutoPlaywrightOpenAI(model="gpt-4o-mini", api_key="OPENAI_API_KEY_HERE")


# Define a Pydantic model for a person structure
class Person(BaseModel):
    first_name: str
    last_name: str
    username: str


# Define a Pydantic model to store the people from the table
class Table(BaseModel):
    people: List[Person]


# The main function that performs the sequence of operations in the browser
def main():
    # Launch Playwright in an asynchronous context
    with sync_playwright() as playwright:
        chromium = playwright.chromium

        # Launch the Chromium browser in non-headless mode (i.e., the browser UI is visible)
        browser = chromium.launch(headless=False)
        page = browser.new_page()

        # Open the test e-commerce website
        page.goto("https://webscraper.io/test-sites/tables")

        # Select people from the table and return data as a Pydantic model (Table)
        # The AI model analyzes the page and extracts the relevant price
        table = ai.auto("Return people from the table", page, Table)

        # People in the table
        print(table.people)

        # Close the page
        page.close()


# Run the main function synchronously
main()

```

## Supported actions
### Action
```python
ai.auto("Click on pricing button", page)
```


### Query / Assert
```python
# Define a Pydantic model for a person structure
class Person(BaseModel):
    first_name: str
    last_name: str
    username: str


# Define a Pydantic model to store the people from the table
class Table(BaseModel):
    people: List[Person]

# Select people from the table and return data as a Pydantic model (Table)
# The AI model analyzes the page and extracts the relevant price
table = ai.auto("Return people from the table", page, Table)

# People in the table
print(table.people)

```

## Supported Playwright Actions

Here is a list of supported actions:

- add_init_script
- bring_to_front
- click
- close
- dblclick
- dispatch_event
- evaluate
- fill
- focus
- go_back
- go_forward
- goto
- hover
- press
- reload
- screenshot
- set_content
- set_viewport_size
- tap
- type
- uncheck
- wait_for_event
- wait_for_load_state
- wait_for_selector
- wait_for_timeout
- wait_for_url

## Why use Auto Playwright Python?

| Aspect                         | Conventional Approach                                                               | Testing with Auto Playwright                                                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Coupling with Markup**       | Strongly linked to the application's markup.                                        | Eliminates the use of selectors; actions are determined by the AI assistant at runtime.                                      |
| **Speed of Implementation**    | Slower implementation due to the need for precise code translation for each action. | Rapid test creation using simple, plain text instructions for actions and assertions.                                        |
| **Handling Complex Scenarios** | Automating complex scenarios is challenging and prone to frequent failures.         | Facilitates testing of complex scenarios by focusing on the intended test outcomes.                                          |
| **Test Writing Timing**        | Can only write tests after the complete development of the functionality.           | Enables a Test-Driven Development (TDD) approach, allowing test writing concurrent with or before functionality development. |

## Implementation

The library optimizes AI query costs by shortening the HTML code before sending the query, reducing the token count and lowering costs associated with OpenAI and DeepSeek models.

## Links

- [Documentation](#) (soon)
- [GitHub](https://github.com/Nohet/autoplaywright-python)

---

Made with ❤️ by Nohet.
