from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict\

config = {
    "torch_device": "cpu",
    "output_format": "markdown",
    "layout_batch_size": 4,
    "detection_batch_size": 4,
    "ocr_batch_size": 4,
    "recognition_batch_size": 4,
    "equation_batch_size": 4,
    "table_rec_batch_size": 4,
}
config_parser = ConfigParser(config)

converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service(),
)
rendered = converter("TSLA-Q2-2025-Update.pdf")
with open("./output/extracted.md", "w") as f:
    f.write(rendered.markdown)
