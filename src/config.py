import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    JIRA_SERVER = os.getenv("JIRA_SERVER")
    JIRA_USER = os.getenv("JIRA_USER")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

    ADO_ORG = os.getenv("ADO_ORG")
    ADO_PROJECT = os.getenv("ADO_PROJECT")
    ADO_REPO = os.getenv("ADO_REPO")
    ADO_PAT = os.getenv("ADO_PAT")  # for CI

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
