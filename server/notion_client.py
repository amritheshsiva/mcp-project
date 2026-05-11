from notion_client import Client
from decouple import config
NOTION_TOKEN = config("NOTION_TOKEN")
PAGE_ID = config("NOTION_PAGE_ID")
notion = Client(auth=NOTION_TOKEN)
def get_page_content():
    response = notion.blocks.children.list(PAGE_ID)
    return response