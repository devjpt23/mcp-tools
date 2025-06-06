from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio
import os
from dotenv import load_dotenv
from groq import Groq
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()


server_parameters = StdioServerParameters(
    command="uv", args=["run", "/home/devjpt23/Desktop/mcp/mcp-tools/server.py"]
)

model = ChatGroq(model="llama-3.1-8b-instant")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

async def main():
    async with stdio_client(server_parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            agent = create_react_agent(model=model, tools=tools)
            agent_response = await agent.ainvoke(
                {"messages": "what is the stock price for TSLA?"}
            )
            return (agent_response)

if __name__ == "__main__":
    asyncio.run(main())
