import json
import os

from typing import Any, List, Optional, Type, Union
from json.decoder import JSONDecodeError

from openai import Client, BadRequestError, RateLimitError, APIError
from openai.types import AllModels

from pydantic import ValidationError

from autoplaywright.prompt import prepare_init_prompt, prepare_auto_prompt
from autoplaywright.types import PydanticModel


class AutoPlaywrightOpenAI:
    """
    A class to automate Playwright steps using ChatGPT(OpenAI)'s API.
    """

    def __init__(
            self,
            model: AllModels,
            api_key: Optional[str] = None,
            **kwargs
    ):
        """
        Initialize the AutoPlaywrightOpenAI instance.

        Args:
            model: The OpenAI model identifier to use for completions
            api_key: OpenAI API key (falls back to OPENAI_API_KEY environment variable if None)
            **kwargs: Additional arguments to pass to the Client constructor

        Raises:
            ValueError: If neither api_key parameter nor OPENAI_API_KEY env var is provided
        """
        self.model = model

        # Initialize the conversation context with the system prompt
        self.__context = [{"role": "developer", "content": prepare_init_prompt()}]

        # Get API key from parameter or environment variable
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key must be provided either as a parameter or via OPENAI_API_KEY environment variable")

        # Initialize the OpenAI client
        self.__client = Client(api_key=api_key, **kwargs)

    def auto(
            self,
            prompt: Union[str, List[str]],
            page: Any,  # Using Any because we don't have the Playwright Page type
            output_format: Optional[Type[PydanticModel]] = None
    ) -> Optional[Union[PydanticModel, List[Optional[PydanticModel]]]]:
        """
        Execute automated browser actions based on natural language prompts.

        Args:
            prompt: String or list of strings containing natural language instructions
            page: Playwright Page object to perform actions on
            output_format: Optional Pydantic model class for structured output data

        Returns:
            Single PydanticModel instance, list of PydanticModel instances, or None
            depending on input and configuration

        Raises:
            ValueError: If prompt is empty or page is invalid
            RuntimeError: If communication with OpenAI API fails
            TypeError: If output validation fails
        """

        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if not page:
            raise ValueError("Page object must be provided")

        if isinstance(prompt, list):
            if not prompt:
                return []

            results = []
            for single_prompt in prompt:
                result = self.auto(single_prompt, page, output_format)
                results.append(result)
            return results

        try:
            page_html = page.inner_html("html")
        except Exception as e:
            raise ValueError(f"Failed to extract HTML from page: {str(e)}")

        self.__context.append({
            "role": "user",
            "content": prepare_auto_prompt(prompt, page_html, output_format)
        })

        try:
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=self.__context,
                response_format={
                    'type': 'json_object'
                }
            )
        except RateLimitError as e:
            self.__context.pop()
            raise RuntimeError(f"OpenAI API rate limit exceeded: {str(e)}")
        except BadRequestError as e:
            self.__context.pop()
            raise ValueError(f"Invalid request to OpenAI API: {str(e)}")
        except APIError as e:
            self.__context.pop()
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.__context.pop()
            raise RuntimeError(f"Unexpected error when calling OpenAI API: {str(e)}")

        try:
            result_dict = json.loads(response.choices[0].message.content)

            self.__context.append({"role": "assistant", "content": str(result_dict)})

        except JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response from OpenAI: {str(e)}, content: {result_dict}")
        except Exception as e:
            raise RuntimeError(f"Error processing OpenAI response: {str(e)}")

        actions = result_dict.get("actions", [])
        for action in actions:
            try:
                method_name = action.get("name")
                args = action.get("args", [])

                if not method_name:
                    continue

                method = getattr(page, method_name, None)

                if method and callable(method):
                    method(*args)
                else:
                    print(f"Warning: Method '{method_name}' not found on page object or not callable")

            except Exception as e:
                print(f"Error executing action '{action.get('name', 'unknown')}': {str(e)}")

        output_data = result_dict.get("outputData")

        if output_data and output_format:
            try:
                return output_format.model_validate(output_data)
            except ValidationError as e:
                raise TypeError(f"Output data validation failed: {str(e)}")

        return None
