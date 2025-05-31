# terminaide/core/index_page.py

"""
Index page functionality for Terminaide.

This module provides the IndexPage class which allows developers to create
navigable menu pages with ASCII art titles, keyboard navigation, and optional
grouping for organizing terminal routes.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import pyfiglet

logger = logging.getLogger("terminaide")


class MenuItem:
    """Single menu item with path and title."""

    def __init__(self, path: str, title: str):
        """
        Initialize a menu item.

        Args:
            path: The URL path (can be internal route or external URL)
            title: Display title for the menu item
        """
        self.path = path
        self.title = title

    def is_external(self) -> bool:
        """Check if this is an external URL."""
        return self.path.startswith(("http://", "https://"))

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {"path": self.path, "title": self.title}


class MenuGroup:
    """Group of menu items with optional name."""

    def __init__(self, menu: List[Dict[str, str]], name: Optional[str] = None):
        """
        Initialize a menu group.

        Args:
            menu: List of menu items as dictionaries
            name: Optional group name (shown when group is active)
        """
        self.name = name
        self.menu_items = [MenuItem(**item) for item in menu]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"menu": [item.to_dict() for item in self.menu_items]}
        if self.name:
            result["name"] = self.name
        return result


class IndexPage:
    """
    Configuration for an index/menu page.

    IndexPage allows creating navigable menu pages with ASCII art titles,
    keyboard navigation, and optional grouping. It can be used as a route
    type alongside scripts and functions in serve_apps().
    """

    def __init__(
        self,
        # Content
        menu: Optional[List[Dict[str, str]]] = None,
        groups: Optional[List[Dict[str, Any]]] = None,
        subtitle: Optional[str] = None,
        instructions: Optional[str] = None,
        # Title/ASCII options
        title: Optional[str] = None,
        page_title: Optional[str] = None,
        ascii_art: Optional[str] = None,
        ascii_font: str = "ansi-shadow",  # Changed default to ansi-shadow
        supertitle: Optional[str] = None,
        # Group cycling
        cycle_key: str = "shift+p",
        # Assets
        preview_image: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize an IndexPage.

        Args:
            menu: Simple list of menu items (use this OR groups, not both)
            groups: List of menu groups for multiple sections
            subtitle: Text paragraph below the title
            instructions: Optional navigation instructions (if not provided, no instructions shown)
            title: Text to convert to ASCII art
            page_title: Browser tab title (defaults to title)
            ascii_art: Pre-made ASCII art (alternative to generated)
            ascii_font: Pyfiglet font name for ASCII generation (default: ansi-shadow)
            supertitle: Regular text above ASCII art
            cycle_key: Key combination to cycle between groups
            preview_image: Path to preview image for social media

        Raises:
            ValueError: If both menu and groups are provided, or neither
        """
        # Load custom fonts before validation
        self._load_custom_fonts()

        # Validation: must have either menu or groups, not both
        if (menu is None) == (groups is None):
            raise ValueError(
                "Must provide either 'menu' or 'groups', but not both. "
                "Use 'menu' for a simple single menu, or 'groups' for multiple sections."
            )

        # Convert menu items
        if menu:
            self.menu_items = [MenuItem(**item) for item in menu]
            self.groups = None
        else:
            self.menu_items = None
            self.groups = [MenuGroup(**g) for g in groups]

        # Store text/title options
        self.subtitle = subtitle
        self.instructions = instructions  # No default value
        self.title = title
        self.page_title = page_title or title or "Index"
        self.ascii_art = ascii_art
        self.ascii_font = ascii_font
        self.supertitle = supertitle

        # Group cycling configuration
        self.cycle_key = cycle_key

        # Handle preview image
        if preview_image:
            self.preview_image = Path(preview_image)
        else:
            self.preview_image = None

        # Validate cycle_key format
        self._validate_cycle_key()

    def _load_custom_fonts(self) -> None:
        """Load custom font files bundled with terminaide."""
        try:
            # Get the misc directory
            misc_dir = Path(__file__).parent / "misc"

            logger.debug(f"Looking for fonts in: {misc_dir}")

            if misc_dir.exists():
                # Store the paths to custom fonts
                self._custom_font_paths = {}

                for font_file in misc_dir.glob("*.flf"):
                    # Use the exact filename (case-sensitive)
                    font_name = font_file.stem  # Don't convert to lowercase yet
                    font_name_lower = font_name.lower()

                    # Store both the original case and lowercase versions
                    self._custom_font_paths[font_name] = str(font_file)
                    self._custom_font_paths[font_name_lower] = str(font_file)

                    # Also try common variations
                    if "-" in font_name:
                        # Handle "ANSI-Shadow" vs "ansi-shadow" vs "ansi_shadow"
                        font_name_underscore = font_name.replace("-", "_").lower()
                        self._custom_font_paths[font_name_underscore] = str(font_file)

                    logger.info(
                        f"Loaded custom font: '{font_name}' (and '{font_name_lower}') from {font_file}"
                    )
            else:
                logger.warning(f"Misc directory does not exist: {misc_dir}")
                self._custom_font_paths = {}

        except Exception as e:
            logger.warning(f"Failed to scan for custom fonts: {e}")
            self._custom_font_paths = {}

    def _validate_cycle_key(self) -> None:
        """Validate the cycle key format."""
        valid_modifiers = {"shift", "ctrl", "alt", "meta"}
        parts = self.cycle_key.lower().split("+")

        if len(parts) != 2:
            raise ValueError(
                f"cycle_key must be in format 'modifier+key', got: {self.cycle_key}"
            )

        modifier, key = parts
        if modifier not in valid_modifiers:
            raise ValueError(
                f"Invalid modifier in cycle_key. Must be one of: {valid_modifiers}"
            )

        if not key or len(key) != 1:
            raise ValueError(
                f"Invalid key in cycle_key. Must be a single character, got: {key}"
            )

    def generate_ascii_title(self) -> Optional[str]:
        """
        Generate ASCII art from title text using pyfiglet.

        Returns:
            ASCII art string, or None if generation fails
        """
        if not self.title:
            return None

        try:
            import pyfiglet

            # Check if we have a custom font path for the requested font
            custom_font_path = getattr(self, "_custom_font_paths", {}).get(
                self.ascii_font
            )

            if custom_font_path:
                # Try using the font file path directly
                try:
                    # pyfiglet.figlet_format can accept a font file path
                    ascii_text = pyfiglet.figlet_format(
                        self.title, font=custom_font_path
                    )
                    logger.debug(f"Using custom font from: {custom_font_path}")
                except Exception as e:
                    logger.warning(f"Failed to use custom font path directly: {e}")
                    # Fall back to standard
                    ascii_text = pyfiglet.figlet_format(self.title, font="standard")
            else:
                # Try to use the font normally (from pyfiglet's built-in fonts)
                try:
                    ascii_text = pyfiglet.figlet_format(
                        self.title, font=self.ascii_font
                    )
                except Exception as e:
                    # Fall back to standard if font not found
                    logger.warning(
                        f"Font '{self.ascii_font}' not found, using 'standard'. Error: {e}"
                    )
                    ascii_text = pyfiglet.figlet_format(self.title, font="standard")

            # Split into lines
            lines = ascii_text.splitlines()

            # Remove trailing blank lines
            while lines and not lines[-1].strip():
                lines.pop()

            # Add exactly one blank line at the end (optional - for spacing)
            lines.append("")

            return "\n".join(lines)

        except ImportError:
            logger.warning("pyfiglet not installed. Install with: pip install pyfiglet")
            return None
        except Exception as e:
            logger.warning(f"Failed to generate ASCII art: {e}")
            return None

    def get_all_menu_items(self) -> List[MenuItem]:
        """
        Get all menu items as a flat list.

        Returns:
            List of all MenuItem objects across all groups
        """
        if self.menu_items:
            return self.menu_items

        all_items = []
        if self.groups:
            for group in self.groups:
                all_items.extend(group.menu_items)
        return all_items

    def to_template_context(self) -> Dict[str, Any]:
        """
        Convert to dictionary for template rendering.

        Returns:
            Dictionary with all data needed for Jinja2 template
        """
        # Generate ASCII title if needed and not provided
        title_ascii = None
        if not self.ascii_art and self.title:
            title_ascii = self.generate_ascii_title()

        # Prepare groups data for JavaScript
        if self.groups:
            groups_data = [group.to_dict() for group in self.groups]
            has_groups = True
        else:
            # Single menu becomes a single unnamed group
            groups_data = [{"menu": [item.to_dict() for item in self.menu_items]}]
            has_groups = False

        # Count total items for grid sizing hints
        total_items = len(self.get_all_menu_items())

        return {
            "page_title": self.page_title,
            "ascii_art": self.ascii_art,
            "title_ascii": title_ascii,
            "supertitle": self.supertitle,
            "subtitle": self.subtitle,
            "instructions": self.instructions,
            "has_groups": has_groups,
            "groups_json": groups_data,
            "cycle_key": self.cycle_key,
            "total_items": total_items,
            # Pass the original title for fallback display
            "title": self.title,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        item_count = len(self.get_all_menu_items())
        group_count = len(self.groups) if self.groups else 1
        return (
            f"IndexPage(title='{self.title}', "
            f"items={item_count}, groups={group_count})"
        )
