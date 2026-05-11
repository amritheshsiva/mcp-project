import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # How to start the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.server"]
    )
    # Start server process and open communication channel
    async with stdio_client(server_params) as (read, write):
        # Create MCP client session
        async with ClientSession(read, write) as session:
            print("\nInitializing MCP Connection...\n")
            # MCP handshake
            await session.initialize()
            print("MCP Connected Successfully!\n")
            # Discover available tools dynamically
            tools = await session.list_tools()
            print("Available Tools:\n")
            for tool in tools.tools:
                print(f"- {tool.name}")
            print("\n" + "=" * 50)

            # Call GitHub MCP Tool

            print("\nCalling GitHub Tool: list_files\n")
            github_result = await session.call_tool(
                "list_files",
                {}
            )
            print("GitHub Tool Result:\n")
            print(github_result)
            print("\n" + "=" * 50)

            # Call Notion MCP Tool

            print("\nCalling Notion Tool: get_notion_page\n")
            notion_result = await session.call_tool(
                "get_notion_page",
                {}
            )
            print("Notion Tool Result:\n")
            print(notion_result)

            print("\n" + "=" * 50)


asyncio.run(main())