from pydantic import BaseModel


class CheckResult(BaseModel):
    entity: str
    doesExist: bool


class OpenAICheckResponse(BaseModel):
    check_results: list[CheckResult]


class WorkExperience(BaseModel):
    job_title: str
    company: str
    location: str
    duration: str
    job_summary: list[str]


class OpenAIResponse(BaseModel):
    educ_info: list[str]
    work_experience: list[WorkExperience]
