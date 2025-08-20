from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import os
from pathlib import Path

# OCR-specific imports from your existing code
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

class OCRInput(BaseModel):
    """Input schema for OCR Tool."""
    pdf_path: str = Field(..., description="Path to the PDF file to extract text from")
    output_path: Optional[str] = Field(None, description="Optional output path for markdown file. If not provided, returns content directly")
    torch_device: Optional[str] = Field("cpu", description="Device to use for processing (cpu/cuda)")

class PDFToMarkdownTool(BaseTool):
    name: str = "PDF to Markdown OCR Tool"
    description: str = (
        "Extracts text from PDF files and converts it to markdown format using advanced OCR. "
        "Handles complex layouts, tables, equations, and maintains document structure. "
        "Returns either the markdown content or saves to a specified file path."
    )
    args_schema: Type[BaseModel] = OCRInput

    def _run(self, pdf_path: str, output_path: Optional[str] = None, torch_device: str = "cpu") -> str:
        try:
            # Validate input file exists
            if not os.path.exists(pdf_path):
                return f"Error: PDF file not found at {pdf_path}"
            
            # Validate file extension
            if not pdf_path.lower().endswith('.pdf'):
                return f"Error: File {pdf_path} is not a PDF file"
            
            # Configure the OCR settings
            config = {
                "torch_device": torch_device,
                "output_format": "markdown",
                "layout_batch_size": 4,
                "detection_batch_size": 4,
                "ocr_batch_size": 4,
                "recognition_batch_size": 4,
                "equation_batch_size": 4,
                "table_rec_batch_size": 4,
            }
            
            # Initialize the converter
            config_parser = ConfigParser(config)
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service(),
            )
            
            # Convert PDF to markdown
            rendered = converter(pdf_path)
            
            # Handle output
            if output_path:
                # Ensure output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                # Save to file
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(rendered.markdown)
                
                return f"PDF successfully converted to markdown and saved to: {output_path}"
            else:
                # Return content directly
                return f"PDF converted successfully. Markdown content:\n\n{rendered.markdown}"
                
        except ImportError as e:
            return f"Error: Missing required dependencies. Please install marker-pdf: {str(e)}"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
