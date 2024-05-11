from openai import OpenAI
import os
from .prompts import *

# from dotenv import load_dotenv
# load_dotenv()

open_ai_token = os.getenv("OPEN_AI_TOKEN")
if open_ai_token is None:
    print("Please set the OPEN_AI_TOKEN environment variable in the .env webhook_commands")
    exit()

client = OpenAI(api_key=open_ai_token)


def parse_resume(resume_text):
    return make_call(parse_resume_prompt, resume_text)


def check_companies(companies_list):
    concatenated_companies_string = ", ".join(companies_list)
    return make_call(check_companies_prompt, concatenated_companies_string)


def check_education(educ_list):
    concatenated_educ_string = ", ".join(educ_list)
    return make_call(check_education_prompt, concatenated_educ_string)


def make_call(prompt, resume_text):
    request_text = prompt + '\n' + resume_text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": request_text}
        ]
    )
    return response.choices[0].message.content
