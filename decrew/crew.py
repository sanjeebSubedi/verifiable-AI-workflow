import hashlib
import os
from typing import List, Type

import requests
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    FileWriterTool,
    ScrapeWebsiteTool,
    SerperDevTool,
)
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from decrew.tools.download_tool import DownloadTool
from decrew.tools.ocr_tool import PDFToMarkdownTool

load_dotenv()

# llm = LLM(
#     model="ollama/qwen3:4b",
#     base_url="http://localhost:11434",
#     temperature=0.7,
#     seed=42,
# )

llm = LLM(
    model="openai/gpt-4",  # call model by provider/model_name
)


class SourcerResponse(BaseModel):
    local_file_path: str = Field(
        ..., description="The path to the saved PDF file on the local system."
    )
    source_url: str = Field(
        ..., description="The URL from which the document was downloaded."
    )
    input_data_hash: str = Field(
        ..., description="The calculated SHA-256 hash of the document."
    )
    validation_summary: str = Field(
        ..., description="A brief sentence confirming the source's authenticity."
    )


@CrewBase
class DecentralizedCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def sourcing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["sourcing_agent"],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                FileWriterTool(),
                FileReadTool(),
                DownloadTool(),
            ],
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=False,
        )

    @agent
    def analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst_agent"],
            tools=[PDFToMarkdownTool(), FileReadTool(), FileWriterTool()],
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=False,
        )

    @task
    def source_document(self) -> Task:
        return Task(
            config=self.tasks_config["tasks"]["source_and_validate_document"],
            agent=self.sourcing_agent(),
            output_json=SourcerResponse,
        )

    @task
    def summarize_document(self) -> Task:
        return Task(
            config=self.tasks_config["tasks"]["analyze_document_and_generate_report"],
            agent=self.analyst_agent(),
            context=[self.source_document()],
        )

    @crew
    def decentralized_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # planning=True,
        )


if __name__ == "__main__":
    inputs = {"company_name": "nvidia"}
    crew = DecentralizedCrew()
    crew.decentralized_crew().kickoff(inputs=inputs)
    print("Crew ran successfully!!")
