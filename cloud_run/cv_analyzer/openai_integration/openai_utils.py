from .openai_responses import *
import json
from pydantic import parse_obj_as


def parse_open_ai_response(json_data: str) -> OpenAIResponse:
    try:
        return parse_obj_as(OpenAIResponse, json.loads(json_data))

    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None


def parse_open_ai_check_response(json_data: str) -> OpenAICheckResponse:
    try:
        return parse_obj_as(OpenAICheckResponse, json.loads(json_data))

    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None
