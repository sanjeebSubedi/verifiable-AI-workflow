from pydantic import BaseModel
from pydantic import Field
from crewai.tools import BaseTool
from typing import Type
import os
import requests
import hashlib

class DownloadInput(BaseModel):
    url: str = Field(..., description="URL of the file to download")
    filename: str = Field(..., description="Local filename to save the file")


class DownloadTool(BaseTool):
    name: str = "Download File Tool"
    description: str = (
        "Downloads a file from a URL and saves it locally, returning the file path and SHA-256 hash"
    )
    args_schema: Type[BaseModel] = DownloadInput

    def _run(self, url: str, filename: str) -> str:
        try:
            os.makedirs("downloads", exist_ok=True)
            file_path = os.path.join("downloads", filename)

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            hash_value = sha256_hash.hexdigest()

            return f"File downloaded successfully. Path: {file_path}, SHA-256: {hash_value}"

        except Exception as e:
            return f"Error downloading file: {str(e)}"
