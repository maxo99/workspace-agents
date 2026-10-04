import base64
from pathlib import Path

import litellm
from dotenv import load_dotenv
from IPython.display import Markdown, display


class PolicyAgent:
    def __init__(
        self,
        model: str = "gpt-4.1-mini",
    ) -> None:
        load_dotenv()
        self.model = model
        self.system_prompt = """You are an expert insurance agent designed to assist with
                                    coverage queries. Use the provided documents to answer questions
                                    about insurance policies. If the information is not available in
                                    the documents, respond with 'I don't know'"""

    def query(
        self,
        prompt: str,
        pdf_path: str | None = None,
    ) -> litellm.ModelResponse:
        pdf_data = None
        user_messages = []
        if pdf_path is not None:
            with Path(pdf_path).open("rb") as file:
                pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

            user_messages.append(
                {
                    "type": "file",
                    "file": {
                        "filename": Path(pdf_path).name,
                        "file_data": f"data:application/pdf;base64,{pdf_data}",
                    },
                },
            )
        user_messages.append(
            {
                "type": "text",
                "text": prompt,
            },
        )

        response = litellm.completion(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_messages},
            ],
        )
        return response

    @staticmethod
    def display_response(response):
        response_text = response.choices[0].message.content.replace("$", r"\\$")
        display(Markdown(response_text))
