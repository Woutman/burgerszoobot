import markdown
import bleach

def convert_markdown_to_html(markdown_text: str) -> str:
    raw_html = markdown.markdown(markdown_text)

    # Sanitize HTML to ensure safe rendering
    allowed_tags = set(bleach.ALLOWED_TAGS).union(['p', 'pre', 'code', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'blockquote'])
    allowed_attributes = {'a': ['href', 'title'], 'img': ['src', 'alt']}
    sanitized_html = bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attributes)

    return sanitized_html