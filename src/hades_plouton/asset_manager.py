"""Centralised asset resolution and image loading for Hades.

Every image the GUI uses (window/taskbar icon, logos, in-window images) is registered here with a default path. Any of them can be overridden by passing an ``overrides`` dict to :class:`AssetManager`.
"""

import os
from tkinter import PhotoImage
from hades.utils import get_asset_path

# Default filenames — override any of these via AssetManager(overrides={...})
DEFAULT_ASSETS = {
    "icon":       
        ("hades_plouton.assets", "hades_icon_dark.ico"),
    "logo_light":
        ("hades_plouton.assets", "HadesLogo_Light_Icon_Transparent_100px.png"),
    "logo_dark":
        ("hades_plouton.assets", "HadesLogo_Dark_Icon_Transparent_100px.png"),
    "pdf_template":
        ("hades.assets.pdf_assets", "template.typ"),
}

class AssetManager:
    """Resolves and caches all image assets."""

    def __init__(self) -> None:
        """Initialise the asset manager and resolve all default paths."""
        self.paths: dict[str, str] = {}
        for key, default in DEFAULT_ASSETS.items():
            # Use the bundled defaults
            self.paths[key] =  get_asset_path(default[0], default[1])

        # Keep PhotoImage refs alive to protect them from garbage collection
        self._image_cache: dict[str, PhotoImage] = {}

    def path(self, key: str) -> str:
        """Return the resolved filesystem path for an asset key."""
        return self.paths.get(key, "")

    def icon(self) -> str:
        """Convenience accessor for the window/taskbar icon path."""
        return self.paths.get("icon", "")

    def load_image(self, key: str) -> PhotoImage | None:
        """Load (and cache) an image by key. Returns None if unavailable."""
        if key in self._image_cache:
            return self._image_cache[key]

        path = self.paths.get(key)
        if path and os.path.exists(path):
            try:
                img = PhotoImage(file=path)
                self._image_cache[key] = img
                return img
            except Exception as exc:  # noqa: BLE001
                print(f"Warning: failed to load image '{key}' ({path}): {exc}")
        return None
