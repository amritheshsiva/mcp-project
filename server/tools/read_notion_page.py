from server.notion_client import get_block_children, get_page_content


def _plain_text(rich_text: list[dict]) -> str:
    return "".join(item.get("plain_text", "") for item in rich_text).strip()


def _block_text(block: dict) -> str | None:
    block_type = block.get("type")
    value = block.get(block_type, {})

    text_blocks = {
        "paragraph",
        "heading_1",
        "heading_2",
        "heading_3",
        "bulleted_list_item",
        "numbered_list_item",
        "quote",
        "callout",
        "code",
        "toggle",
    }

    if block_type in text_blocks:
        text = _plain_text(value.get("rich_text", []))
        if not text:
            return None

        if block_type == "heading_1":
            return f"# {text}"
        if block_type == "heading_2":
            return f"## {text}"
        if block_type == "heading_3":
            return f"### {text}"
        if block_type == "bulleted_list_item":
            return f"- {text}"
        if block_type == "numbered_list_item":
            return f"1. {text}"
        if block_type == "quote":
            return f"> {text}"
        if block_type == "code":
            language = value.get("language", "")
            return f"```{language}\n{text}\n```"
        return text

    if block_type == "to_do":
        text = _plain_text(value.get("rich_text", []))
        checked = "x" if value.get("checked") else " "
        return f"- [{checked}] {text}" if text else None

    if block_type == "table_row":
        cells = [_plain_text(cell) for cell in value.get("cells", [])]
        return " | ".join(cells).strip() or None

    if block_type == "child_page":
        title = value.get("title", "").strip()
        return f"Page: {title}" if title else None

    return None


def _read_blocks(blocks: list[dict]) -> list[str]:
    content = []

    for block in blocks:
        text = _block_text(block)
        if text:
            content.append(text)

        if block.get("has_children"):
            content.extend(_read_blocks(get_block_children(block["id"])))

    return content


def read_notion_page():
    content = _read_blocks(get_page_content())
    return {
        "content": content,
        "text": "\n".join(content),
    }
