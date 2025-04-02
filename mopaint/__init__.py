import base64
from pathlib import Path
import anywidget
import traitlets
from io import BytesIO
from PIL import Image


def base64_to_pil(base64_string):
    """Convert a base64 string to PIL Image"""
    # Remove the data URL prefix if it exists
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decode base64 string
    img_data = base64.b64decode(base64_string)

    # Create PIL Image from bytes
    return Image.open(BytesIO(img_data))


class Paint(anywidget.AnyWidget):
    """Initialize a Draw widget based on tldraw.
    """
    _esm = Path(__file__).parent / 'static' / 'draw.js'
    _css = Path(__file__).parent / 'static' / 'styles.css'
    base64 = traitlets.Unicode("").tag(sync=True)
    cache_path = traitlets.Unicode("").tag(sync=True)
    
    def __init__(self, width=1000, height=450, cache_path=None, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        if cache_path:
            self.cache_path = str(cache_path)
            # Load from cache if exists
            if Path(cache_path).exists():
                with open(cache_path, 'r') as f:
                    self.base64 = f.read()

    @traitlets.observe('base64')
    def _on_base64_change(self, change):
        """Called when base64 trait changes"""
        if self.cache_path and change['new']:
            # Ensure parent directory exists
            cache_file = Path(self.cache_path)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            # Save to cache
            with open(cache_file, 'w') as f:
                f.write(change['new'])

    def get_pil(self):
        if not self.base64:
            raise ValueError("No base64 image data available, make sure you draw something first.")
        return base64_to_pil(self.base64)

    def get_base64(self) -> str:
        return self.base64