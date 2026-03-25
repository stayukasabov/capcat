
import yaml
from pathlib import Path

class SourceConfigGenerator:
    """
    Generates and saves YAML configuration files for new config-driven sources.
    """

    def __init__(self, source_metadata: dict):
        """
        Args:
            source_metadata: A dictionary containing the required data:
                - source_id (str): The unique identifier for the source.
                - display_name (str): The user-facing name.
                - base_url (str): The base URL of the source website.
                - rss_url (str): The URL of the RSS feed.
                - category (str): The category the source belongs to.
        """
        self.metadata = source_metadata

    def generate_yaml_content(self) -> str:
        """
        Generates the YAML configuration as a string.

        Returns:
            A string containing the YAML configuration.
        """
        # Defaulting to use the RSS summary for both article and content
        # as per the PRD. This is the simplest, most reliable initial setup.
        config_data = {
            "display_name": self.metadata["display_name"],
            "base_url": self.metadata["base_url"],
            "category": self.metadata["category"],
            "article_count": self.metadata.get("article_count", 30),
            "discovery": {
                "method": "rss",
                "rss_url": self.metadata["rss_url"],
            },
            "article_selectors": ["summary"],
            "content_selectors": ["summary"],
            "author_selectors": [],
            "publish_date_selectors": [],
        }

        base_yaml = yaml.dump(config_data, sort_keys=False, default_flow_style=False)

        image_processing_block = (
            "\n"
            "# Image downloading configuration — edit to tune for this source.\n"
            "image_processing:\n"
            "  allow_extensionless: true   # keep true for CDN URLs without .jpg extension\n"
            "  max_images: 10              # maximum images to download per article\n"
            "  # Uncomment to restrict which img tags are used:\n"
            "  # selectors:\n"
            "  #   - article img\n"
            "  #   - .post-content img\n"
            "  # Uncomment to skip logo/avatar/ad images:\n"
            "  # skip_selectors:\n"
            "  #   - .avatar img\n"
            "  #   - .ad img\n"
            "  # Uncomment to skip tiny icons (size in bytes):\n"
            "  # min_image_size: 5000\n"
        )

        return base_yaml + image_processing_block

    def generate_and_save(self, base_path: str) -> str:
        """
        Generates the YAML content and saves it to the specified path.

        Args:
            base_path: The directory where the config file should be saved.

        Returns:
            The full path to the newly created file.
        """
        source_id = self.metadata["source_id"]
        file_path = Path(base_path) / f"{source_id}.yml"

        yaml_content = self.generate_yaml_content()

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(yaml_content)

        return str(file_path)
