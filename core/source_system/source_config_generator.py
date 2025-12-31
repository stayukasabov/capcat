
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
            "discovery": {
                "method": "rss",
                "rss_url": self.metadata["rss_url"],
            },
            "article_selectors": ["summary"],
            "content_selectors": ["summary"],
            "author_selectors": [],
            "publish_date_selectors": [],
        }

        # Use sort_keys=False to maintain a more logical order
        return yaml.dump(config_data, sort_keys=False, default_flow_style=False)

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

        with open(file_path, 'w') as f:
            f.write(yaml_content)

        return str(file_path)
