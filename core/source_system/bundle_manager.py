
from ruamel.yaml import YAML
from pathlib import Path

class BundleManager:
    """
    Manages the addition of sources to bundles in the bundles.yml file,
    preserving comments and structure.
    """

    def __init__(self, bundle_file_path: str):
        """
        Args:
            bundle_file_path: The absolute path to the bundles.yml file.
        """
        self.bundle_file_path = Path(bundle_file_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self._load_data()

    def _load_data(self):
        """Loads the YAML data from the file."""
        try:
            self.data = self.yaml.load(self.bundle_file_path)
        except FileNotFoundError:
            # Handle case where file might not exist, though it should
            self.data = {'bundles': {}}

    def _save_data(self):
        """Saves the modified YAML data back to the file."""
        with open(self.bundle_file_path, 'w') as f:
            self.yaml.dump(self.data, f)

    def get_bundle_names(self) -> list[str]:
        """Returns a list of all available bundle names."""
        return list(self.data.get("bundles", {}).keys())

    def add_source_to_bundle(self, source_id: str, bundle_name: str):
        """
        Adds a source ID to a specified bundle and saves the file.

        Args:
            source_id: The ID of the source to add.
            bundle_name: The name of the bundle to add the source to.

        Raises:
            ValueError: If the bundle_name does not exist.
        """
        bundles = self.data.get("bundles", {})
        if bundle_name not in bundles:
            raise ValueError(f"Bundle '{bundle_name}' not found.")

        if source_id not in bundles[bundle_name]['sources']:
            bundles[bundle_name]['sources'].append(source_id)
            self._save_data()

    def remove_source_from_all_bundles(self, source_id: str) -> list[str]:
        """
        Removes a source ID from all bundles and saves the file.

        Args:
            source_id: The ID of the source to remove.

        Returns:
            List of bundle names that were updated.
        """
        bundles = self.data.get("bundles", {})
        updated_bundles = []

        for bundle_name, bundle_data in bundles.items():
            sources = bundle_data.get('sources', [])
            if source_id in sources:
                sources.remove(source_id)
                updated_bundles.append(bundle_name)

        if updated_bundles:
            self._save_data()

        return updated_bundles

    def create_bundle(
        self,
        bundle_id: str,
        description: str,
        default_count: int = 20,
        sources: list = None
    ) -> None:
        """
        Create new bundle in bundles.yml.

        Args:
            bundle_id: Unique bundle identifier (lowercase_with_underscores)
            description: Bundle description (1-200 chars)
            default_count: Default article count (1-100, default 20)
            sources: Initial source list (optional, default [])

        Raises:
            ValueError: If bundle_id exists or invalid
        """
        if bundle_id in self.data.get('bundles', {}):
            raise ValueError(f"Bundle '{bundle_id}' already exists")

        if sources is None:
            sources = []

        bundles = self.data.setdefault('bundles', {})
        bundles[bundle_id] = {
            'description': description,
            'sources': sources,
            'default_count': default_count
        }
        self._save_data()

    def delete_bundle(self, bundle_id: str) -> None:
        """
        Delete bundle from bundles.yml.

        Args:
            bundle_id: Bundle to delete

        Raises:
            ValueError: If bundle not found or protected
        """
        if bundle_id == 'all':
            raise ValueError("Cannot delete 'all' bundle (system bundle)")

        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        del bundles[bundle_id]
        self._save_data()

    def update_bundle_metadata(
        self,
        bundle_id: str,
        description: str = None,
        default_count: int = None
    ) -> None:
        """
        Update bundle metadata (description and/or default_count).

        Args:
            bundle_id: Bundle to update
            description: New description (optional)
            default_count: New default count (optional)

        Raises:
            ValueError: If bundle not found or no changes provided
        """
        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        if description is None and default_count is None:
            raise ValueError("Must provide at least one field to update")

        bundle = bundles[bundle_id]
        if description is not None:
            bundle['description'] = description
        if default_count is not None:
            bundle['default_count'] = default_count

        self._save_data()

    def get_bundle_details(self, bundle_id: str) -> dict:
        """
        Get detailed information about a bundle.

        Args:
            bundle_id: Bundle to query

        Returns:
            Dictionary with bundle metadata and statistics

        Raises:
            ValueError: If bundle not found
        """
        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        bundle_data = bundles[bundle_id]

        # Calculate category distribution
        from core.source_system.source_registry import get_source_registry
        registry = get_source_registry()

        categories = {}
        for source_id in bundle_data.get('sources', []):
            config = registry.get_source_config(source_id)
            if config:
                category = getattr(config, 'category', 'other')
                categories[category] = categories.get(category, 0) + 1

        return {
            'bundle_id': bundle_id,
            'description': bundle_data.get('description', ''),
            'sources': bundle_data.get('sources', []),
            'default_count': bundle_data.get('default_count', 20),
            'total_sources': len(bundle_data.get('sources', [])),
            'category_distribution': categories
        }

    def list_bundles(self) -> list:
        """
        Get list of all bundles with basic info.

        Returns:
            List of bundle dictionaries with id, description, source_count
        """
        bundles_list = []
        for bundle_id, bundle_data in self.data.get('bundles', {}).items():
            bundles_list.append({
                'bundle_id': bundle_id,
                'description': bundle_data.get('description', ''),
                'source_count': len(bundle_data.get('sources', [])),
                'default_count': bundle_data.get('default_count', 20)
            })

        return sorted(bundles_list, key=lambda x: x['bundle_id'])

    def add_sources_to_bundle(
        self,
        bundle_id: str,
        source_ids: list
    ) -> int:
        """
        Add multiple sources to bundle.

        Args:
            bundle_id: Target bundle
            source_ids: List of source IDs to add

        Returns:
            Number of sources added (excludes duplicates)

        Raises:
            ValueError: If bundle not found
        """
        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        bundle_sources = bundles[bundle_id].get('sources', [])
        added_count = 0

        for source_id in source_ids:
            if source_id not in bundle_sources:
                bundle_sources.append(source_id)
                added_count += 1

        if added_count > 0:
            self._save_data()

        return added_count

    def remove_sources_from_bundle(
        self,
        bundle_id: str,
        source_ids: list
    ) -> int:
        """
        Remove multiple sources from bundle.

        Args:
            bundle_id: Target bundle
            source_ids: List of source IDs to remove

        Returns:
            Number of sources removed

        Raises:
            ValueError: If bundle not found
        """
        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        bundle_sources = bundles[bundle_id].get('sources', [])
        removed_count = 0

        for source_id in source_ids:
            if source_id in bundle_sources:
                bundle_sources.remove(source_id)
                removed_count += 1

        if removed_count > 0:
            self._save_data()

        return removed_count

    def move_source_between_bundles(
        self,
        source_id: str,
        from_bundle_id: str,
        to_bundle_id: str,
        copy_mode: bool = False
    ) -> dict:
        """
        Move or copy source from one bundle to another.

        Args:
            source_id: Source to move/copy
            from_bundle_id: Source bundle
            to_bundle_id: Target bundle
            copy_mode: If True, copy (keep in source). If False, move (remove from source)

        Returns:
            Dictionary with 'added' and 'removed' status

        Raises:
            ValueError: If bundles not found or source not in from_bundle
        """
        bundles = self.data.get('bundles', {})

        if from_bundle_id not in bundles:
            raise ValueError(f"Source bundle '{from_bundle_id}' not found")

        if to_bundle_id not in bundles:
            raise ValueError(f"Target bundle '{to_bundle_id}' not found")

        from_sources = bundles[from_bundle_id].get('sources', [])
        to_sources = bundles[to_bundle_id].get('sources', [])

        if source_id not in from_sources:
            raise ValueError(
                f"Source '{source_id}' not in bundle '{from_bundle_id}'"
            )

        result = {'added': False, 'removed': False}

        # Add to target bundle
        if source_id not in to_sources:
            to_sources.append(source_id)
            result['added'] = True

        # Remove from source bundle (if move mode)
        if not copy_mode:
            from_sources.remove(source_id)
            result['removed'] = True

        self._save_data()
        return result

    def get_source_bundle_memberships(self, source_id: str) -> list:
        """
        Get list of bundles containing a source.

        Args:
            source_id: Source to query

        Returns:
            List of bundle IDs containing the source
        """
        bundles = self.data.get('bundles', {})
        memberships = []

        for bundle_id, bundle_data in bundles.items():
            if source_id in bundle_data.get('sources', []):
                memberships.append(bundle_id)

        return sorted(memberships)

    def bulk_add_by_category(
        self,
        bundle_id: str,
        category: str
    ) -> int:
        """
        Add all sources from a category to bundle.

        Args:
            bundle_id: Target bundle
            category: Source category (tech, news, etc.)

        Returns:
            Number of sources added

        Raises:
            ValueError: If bundle not found
        """
        from core.source_system.source_registry import get_source_registry

        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        registry = get_source_registry()
        bundle_sources = bundles[bundle_id].get('sources', [])
        added_count = 0

        for source_id in registry.get_available_sources():
            config = registry.get_source_config(source_id)
            if config and getattr(config, 'category', None) == category:
                if source_id not in bundle_sources:
                    bundle_sources.append(source_id)
                    added_count += 1

        if added_count > 0:
            self._save_data()

        return added_count

    def bulk_remove_by_category(
        self,
        bundle_id: str,
        category: str
    ) -> int:
        """
        Remove all sources from a category from bundle.

        Args:
            bundle_id: Target bundle
            category: Source category (tech, news, etc.)

        Returns:
            Number of sources removed

        Raises:
            ValueError: If bundle not found
        """
        from core.source_system.source_registry import get_source_registry

        bundles = self.data.get('bundles', {})
        if bundle_id not in bundles:
            raise ValueError(f"Bundle '{bundle_id}' not found")

        registry = get_source_registry()
        bundle_sources = bundles[bundle_id].get('sources', [])
        removed_count = 0

        sources_to_remove = []
        for source_id in bundle_sources:
            config = registry.get_source_config(source_id)
            if config and getattr(config, 'category', None) == category:
                sources_to_remove.append(source_id)

        for source_id in sources_to_remove:
            bundle_sources.remove(source_id)
            removed_count += 1

        if removed_count > 0:
            self._save_data()

        return removed_count
