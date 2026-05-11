# MCP GitHub + Notion AI Assistant

A beginner-friendly hands-on project to learn **MCP (Model Context Protocol)** by building a real AI assistant using:

- MCP Server
- MCP Client
- GitHub API
- Notion API
- Groq LLM
- Python

This project demonstrates how AI agents can dynamically use external tools through MCP.

---

# Features

## GitHub MCP Tools
- List repository files
- Read repository file contents

## Notion MCP Tools
- Read Notion page content
- Retrieve personal/contextual notes

## AI Agent Features
- Dynamic MCP tool discovery
- MCP tool calling
- Multi-tool integration
- Context-aware AI responses
- GitHub + Notion retrieval

---

# MCP Architecture

```text
                 User Question
                        │
                        ▼
                  AI Agent (Groq)
                        │
                 MCP Tool Calls
                        │
                ┌───────▼────────┐
                │   MCP Server   │
                └───────┬────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
     GitHub Tools               Notion Tools

```
