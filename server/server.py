from mcp.server.fastmcp import FastMCP
from server.tools.list_files import get_repo_files
from server.tools.read_file import read_file
from server.tools.read_notion_page import read_notion_page
mcp = FastMCP("GitHub MCP Assistant")
@mcp.tool()
def list_files():
    "List repository files"
    return get_repo_files()


@mcp.tool()
def get_file_content(file_path: str):
    """
    Read a specific repository file by path or name.
    """
    return read_file(file_path)

@mcp.tool()
def get_notion_page():
    """
    Read notion page content
    """
    return read_notion_page()

if __name__ == "__main__":
    mcp.run()
