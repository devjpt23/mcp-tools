from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

import os
import asyncio
from groq import Groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()


server_parameters = StdioServerParameters(
    command="uv", args=["run", "/home/devjpt23/Desktop/mcp/k8s-mcp-server/k8s-mcp-server/server.py"]
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
                {"messages": "Can you create for me a deployment resource yaml file with image named nginx:latest, running on port 80, with deployment named 'devs-deployment' and has 3 replicas"},
        
            )
            return (agent_response)

if __name__ == "__main__":
    asyncio.run(main())


