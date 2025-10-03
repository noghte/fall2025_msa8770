from agents import Agent, Runner, WebSearchTool
import os
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    name="Assistant",
    model="gpt-4o-mini",
    tools=[WebSearchTool()]
)

prompt = "How's weather in Atlanta today? Use site:https://www.accuweather.com/en/us/atlanta/30303/weather-forecast/348181"
result = Runner.run_sync(agent, prompt)
print(result.final_output)