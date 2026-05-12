import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from client.ai_client import ask_llm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text(result) -> str:
    """Extract plain text from an MCP tool result."""
    return result.content[0].text


def _is_file_question(question: str) -> bool:
    keywords = ("inside", "content", "read", "show", "what is in", "what's in", "open")
    q = question.lower()
    return any(k in q for k in keywords)


def _extract_filename(question: str) -> str | None:
    """
    Pull a filename from a question such as:
      "What's inside pi.txt in my GitHub?"
    Returns the token that looks like a filename (contains a '.'), or None.
    """
    for token in question.split():
        token = token.strip("?,'\"")
        if "." in token and not token.startswith("http"):
            return token
    return None


# ---------------------------------------------------------------------------
# Core agent
# ---------------------------------------------------------------------------

# To start MCP server by running : python -m server.server
async def run_agent(user_question: str) -> str:
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.server"],
    )
# Creates communication pipes
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ----------------------------------------------------------------
            # Branch 1: Notion questions
            # ----------------------------------------------------------------
            if "notion" in user_question.lower() or "note" in user_question.lower():
                context = _text(await session.call_tool("get_notion_page", {}))
                prompt = _build_prompt(user_question, context)
                return ask_llm(prompt)

            # ----------------------------------------------------------------
            # Branch 2: "Read this file" questions
            # ----------------------------------------------------------------
            if _is_file_question(user_question):
                filename = _extract_filename(user_question)

                if filename:
                    read_result = await session.call_tool(
                        "get_file_content",
                        {"file_path": filename},
                    )
                    raw = _text(read_result)

                    # The tool may return JSON or plain text
                    try:
                        data = json.loads(raw)
                        if "error" in data:
                            # File not found at root — list files first and retry
                            context = await _find_and_read(session, filename)
                        else:
                            context = f"Contents of `{filename}`:\n\n{data.get('content', raw)}"
                    except json.JSONDecodeError:
                        context = f"Contents of `{filename}`:\n\n{raw}"

                else:
                    # No filename detected — fall back to listing
                    context = _text(await session.call_tool("list_files", {}))

                prompt = _build_prompt(user_question, context)
                return ask_llm(prompt)

            # ----------------------------------------------------------------
            # Branch 3: General repository questions — list files
            # ----------------------------------------------------------------
            context = _text(await session.call_tool("list_files", {}))
            prompt = _build_prompt(user_question, context)
            return ask_llm(prompt)


async def _find_and_read(session: ClientSession, filename: str) -> str:
    """
    List all repo files, find the full path that matches `filename`,
    then read and return its contents.
    """
    list_result = _text(await session.call_tool("list_files", {}))

    try:
        files = json.loads(list_result)
    except json.JSONDecodeError:
        return f"Could not locate `{filename}` in the repository."

    # Match on name or trailing path segment
    matched_path = None
    for f in files if isinstance(files, list) else []:
        entry_name = f.get("name", "") or f.get("path", "").split("/")[-1]
        if entry_name == filename:
            matched_path = f.get("path") or f.get("name")
            break

    if not matched_path:
        return f"`{filename}` was not found in the repository."

    read_result = await session.call_tool("get_file_content", {"file_path": matched_path})
    raw = _text(read_result)

    try:
        data = json.loads(raw)
        content = data.get("content", raw)
    except json.JSONDecodeError:
        content = raw

    return f"Contents of `{matched_path}`:\n\n{content}"


def _build_prompt(question: str, context: str) -> str:
    return f"""You are a helpful assistant with access to GitHub repository data and Notion page data.

User Question:
{question}

Context (retrieved from the relevant MCP tool):
{context}

Answer the question using ONLY the context above. Do not guess or invent content.
If the context contains file or Notion page contents, quote them directly in your answer.
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    user_question = input("\nAsk Question: ")
    response = asyncio.run(run_agent(user_question))
    print("\nAI Response:\n")
    print(response)


if __name__ == "__main__":
    main()


# import asyncio
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# from client.ai_client import ask_llm


# async def run_agent(user_question: str):

#     # Start MCP server
#     server_params = StdioServerParameters(
#         command="python",
#         args=["-m", "server.server"]
#     )

#     # Create MCP connection
#     async with stdio_client(server_params) as (read, write):

#         # Create session
#         async with ClientSession(read, write) as session:

#             # Initialize MCP
#             await session.initialize()

#             # -----------------------------
#             # NOTION QUESTIONS
#             # -----------------------------
#             if "notion" in user_question.lower() or "note" in user_question.lower():

#                 result = await session.call_tool(
#                     "get_notion_page",
#                     {}
#                 )

#                 context = result.content[0].text

#             # -----------------------------
#             # READ FILE QUESTIONS
#             # -----------------------------
#             elif "read" in user_question.lower() or "inside" in user_question.lower():

#                 # Example:
#                 # "read app.py"

#                 words = user_question.split()

#                 filename = None

#                 for word in words:
#                     if "." in word:
#                         filename = word
#                         break

#                 if filename:

#                     result = await session.call_tool(
#                         "get_file_content",
#                         {
#                             "file_path": filename
#                         }
#                     )

#                     context = result.content[0].text

#                 else:
#                     context = "No filename found."

#             # -----------------------------
#             # DEFAULT → LIST FILES
#             # -----------------------------
#             else:

#                 result = await session.call_tool(
#                     "list_files",
#                     {}
#                 )

#                 context = result.content[0].text

#             # -----------------------------
#             # FINAL PROMPT
#             # -----------------------------
#             final_prompt = f"""
# User Question:
# {user_question}

# Retrieved Context:
# {context}

# Answer using only the retrieved context.
# """

#             # Ask LLM
#             response = ask_llm(final_prompt)

#             return response


# def main():

#     user_question = input("\nAsk Question: ")

#     response = asyncio.run(
#         run_agent(user_question)
#     )

#     print("\nAI Response:\n")
#     print(response)


# if __name__ == "__main__":
#     main()
