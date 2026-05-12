from notion_client import Client
from decouple import config

NOTION_TOKEN = config("NOTION_TOKEN")
PAGE_ID = config("NOTION_PAGE_ID")
notion = Client(auth=NOTION_TOKEN)


def get_block_children(block_id: str):
    """Return all child blocks for a Notion block/page."""
    blocks = []
    cursor = None

    while True:
        response = notion.blocks.children.list(block_id=block_id, start_cursor=cursor)
        blocks.extend(response.get("results", []))

        if not response.get("has_more"):
            break

        cursor = response.get("next_cursor")

    return blocks


def get_page_content():
    return get_block_children(PAGE_ID)
