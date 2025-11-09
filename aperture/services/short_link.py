from nanoid import generate
from config import settings


def generate_short_id(size: int = 8) -> str:
    """Generate a short, URL-safe ID."""
    return generate(size=size)


def create_aperture_link(short_id: str, action: str = "why") -> str:
    """
    Create an Aperture link for user interaction.

    Args:
        short_id: The unique identifier for this response
        action: Type of link ('why' or 'edit')

    Returns:
        Full URL for the link
    """
    base_url = f"http://{settings.short_link_domain}" if settings.environment == "development" else f"https://{settings.short_link_domain}"

    if action == "why":
        return f"{base_url}/c/{short_id}"
    elif action == "edit":
        return f"{base_url}/c/{short_id}/edit"
    else:
        return f"{base_url}/c/{short_id}"


def create_embedded_footer(short_id: str) -> str:
    """
    Create HTML footer to embed in LLM responses.

    This is what gets appended to the AI's response.
    """
    why_link = create_aperture_link(short_id, "why")
    edit_link = create_aperture_link(short_id, "edit")

    return f"""

<small style="color: #888; font-size: 11px; margin-top: 12px; display: block;">
  <a href="{why_link}" style="color: #888; text-decoration: none;">💡 Why this response?</a> •
  <a href="{edit_link}" style="color: #888; text-decoration: none;">✏️ Correct my understanding</a>
</small>"""
