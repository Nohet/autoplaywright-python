import json
import os

from typing import Any, List, Optional, Type, Union, Literal
from pydantic import ValidationError

from openai import AsyncClient, BadRequestError, RateLimitError, APIError
from autoplaywright.prompt import prepare_init_prompt, prepare_auto_prompt
from autoplaywright.types import PydanticModel


class AutoPlaywrightDeepSeek:
    """
    A class to automate Playwright steps using DeepSeek's API.
    """

    def __init__(
            self,
            model: Union[Literal["deepseek-reasoner"], Literal["deepseek-chat"], str],
            api_key: Optional[str] = None,
            **kwargs
    ):
        """
        Initialize the AutoPlaywrightDeepSeek instance.

        Args:
            model: The DeepSeek model identifier to use for completions
            api_key: DeepSeek API key (falls back to DEEPSEEK_API_KEY environment variable if None)
            **kwargs: Additional arguments to pass to the AsyncClient constructor

        Raises:
            ValueError: If neither api_key parameter nor DEEPSEEK_API_KEY env var is provided
        """
        self.model = model

        # Initialize the conversation context with the system prompt
        self.__context = [{"role": "system", "content": prepare_init_prompt()}]

        # Get API key from parameter or environment variable
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DeepSeek API key must be provided either as a parameter or via DEEPSEEK_API_KEY environment variable")

        # Initialize the DeepSeek client
        self.__client = AsyncClient(api_key=api_key,
                                    base_url="https://api.deepseek.com",
                                    **kwargs)

    async def auto(
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
            RuntimeError: If communication with DeepSeek API fails
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
                result = await self.auto(single_prompt, page, output_format)
                results.append(result)
            return results

        try:
            page_html = await page.inner_html("html")
        except Exception as e:
            raise ValueError(f"Failed to extract HTML from page: {str(e)}")

        self.__context.append({
            "role": "user",
            "content": prepare_auto_prompt(prompt, page_html, output_format)
        })

        try:
            response = await self.__client.chat.completions.create(
                model=self.model,
                messages=self.__context,
                response_format={
                    'type': 'json_object'
                }
            )
        except RateLimitError as e:
            self.__context.pop()
            raise RuntimeError(f"DeepSeek API rate limit exceeded: {str(e)}")
        except BadRequestError as e:
            self.__context.pop()
            raise ValueError(f"Invalid request to DeepSeek API: {str(e)}")
        except APIError as e:
            self.__context.pop()
            raise RuntimeError(f"DeepSeek API error: {str(e)}")
        except Exception as e:
            self.__context.pop()
            raise RuntimeError(f"Unexpected error when calling DeepSeek API: {str(e)}")

        try:
            result_dict = json.loads(response.choices[0].message.content)

            if not result_dict:
                raise ValueError("Empty response from DeepSeek API")

            self.__context.append({"role": "assistant", "content": str(result_dict)})

        except Exception as e:
            raise RuntimeError(f"Error processing DeepSeek response: {str(e)}")

        actions = result_dict.get("actions", [])
        for action in actions:
            try:
                method_name = action.get("name")
                args = action.get("args", [])

                if not method_name:
                    continue

                method = getattr(page, method_name, None)

                if method and callable(method):
                    await method(*args)
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
