from server.notion_client import get_page_content
def read_notion_page():
    data = get_page_content()
    results = []
    for block in data["results"]:
        if block["type"] == "paragraph":
            text_data = block["paragraph"]["rich_text"]
            if text_data:
                results.append(
                    text_data[0]["plain_text"]
                )
    return {
        "content": results
    }