# import warnings
import os

import google.auth
import google.auth.credentials
import google.auth.transport.requests
import nest_asyncio
from a2a.types import AgentCard
from dotenv import load_dotenv
from google.auth import impersonated_credentials
from google.oauth2 import service_account
from IPython.display import Markdown, display


def setup_env() -> None:
    load_dotenv(override=True)
    nest_asyncio.apply()

    # warnings.filterwarnings("ignore", category=UserWarning)
    # warnings.filterwarnings("ignore", category=FutureWarning)


def display_agent_card(agent_card: AgentCard) -> None:
    """Nicely formats and displays an AgentCard."""

    def esc(text: str) -> str:
        """Escapes pipe characters for Markdown table compatibility."""
        return str(text).replace("|", r"\|")

    # --- Part 1: Main Metadata Table ---
    md_parts = [
        "### Agent Card Details",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Name** | {esc(agent_card.name)} |",
        f"| **Description** | {esc(agent_card.description)} |",
        f"| **Version** | `{esc(agent_card.version)}` |",
        f"| **URL** | [{esc(agent_card.url)}]({agent_card.url}) |",
        f"| **Protocol Version** | `{esc(agent_card.protocol_version)}` |",
    ]

    # --- Part 2: Skills Table ---
    if agent_card.skills:
        md_parts.extend(
            [
                "\n#### Skills",
                "| Name | Description | Examples |",
                "| :--- | :--- | :--- |",
            ]
        )
        for skill in agent_card.skills:
            examples_str = (
                "<br>".join(f"• {esc(ex)}" for ex in skill.examples) if skill.examples else "N/A"
            )
            md_parts.append(
                f"| **{esc(skill.name)}** | {esc(skill.description)} | {examples_str} |"
            )

    # Join all parts and display
    display(Markdown("\n".join(md_parts)))


def gcp_authenticate(
    location: str | None = None,
) -> tuple[google.auth.credentials.Credentials, str]:
    load_dotenv(override=True)

    # 1. Locate the JSON key file
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # SAFETY CHECK: Ensure the file actually exists
    if not key_path or not os.path.exists(key_path):
        # Fallback: Try to look in the current directory if env var is missing
        if os.path.exists("credentials.json"):
            key_path = "credentials.json"
        elif os.path.exists("../credentials.json"):
            key_path = "../credentials.json"
        else:
            raise ValueError(
                "Could not find credentials.json or GOOGLE_APPLICATION_CREDENTIALS env var."
            )

    # 2. Load the file EXPLICITLY with scopes
    source_credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # 3. Create the HTTP Request object
    request = google.auth.transport.requests.Request()

    # 4. Refresh the source credential (The 1-hour token)
    source_credentials.refresh(request)

    # 5. Create Impersonated Credentials (The 2-hour token)
    target_principal = source_credentials.service_account_email

    credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_principal,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        lifetime=7200,  # 2 Hours
        iam_endpoint_override=os.getenv("DLAI_GOOGLE_IAM_ENDPOINT"),
    )

    # 6. Refresh to get the final token
    credentials.refresh(request)

    # Set Env Vars
    os.environ["GOOGLE_CLOUD_PROJECT"] = source_credentials.project_id
    if location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = location

    return credentials, source_credentials.project_id
