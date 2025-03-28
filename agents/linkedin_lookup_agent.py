import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Import necessary modules from LangChain and other libraries
from langchain_openai import ChatOpenAI  # Using DeepSeek API via LangChain
from langchain.prompts.prompt import PromptTemplate  # Allows structured prompts
from langchain_core.tools import Tool  # Used to define tools for the agent
from langchain.agents import create_react_agent, AgentExecutor  # ReAct framework
from langchain import hub  # Used to fetch predefined prompts
from langchain_community.tools.tavily_search import TavilySearchResults  # Tavily search tool


# **Function to search for LinkedIn profiles using Tavily**
# Uses the Tavily search engine
# Builds a smart search query: "John Doe site:linkedin.com/in"
# Filters the results to only LinkedIn profile URLs
# Returns the first match (or a default message if none)

def get_profile_url_tavily(name: str):
    """
    Uses Tavily search engine to find a LinkedIn profile URL based on the given name.
    """
    api_key = os.getenv("TAVILY_API_KEY")  # Fetch Tavily API key from .env
    if not api_key:
        raise ValueError("⚠️ TAVILY_API_KEY is missing. Add it to the .env file!")

    # Initialize Tavily search tool
    search = TavilySearchResults()

    # Perform search for LinkedIn profiles
    query = f"{name} site:linkedin.com/in"
    results = search.run(query)

    # **Extract valid LinkedIn profile URLs**
    linkedin_urls = [result["url"] for result in results if "linkedin.com/in/" in result["url"]]

    return linkedin_urls[0] if linkedin_urls else "LinkedIn profile not found."


# **Function to look up a LinkedIn profile URL based on a person's name**
def lookup(name: str) -> str:
    """
    This function takes a person's name and attempts to find their LinkedIn profile URL.
    It uses an AI model to generate a search query and the Tavily search tool to retrieve the LinkedIn profile.
    """
    # **Retrieve API key for DeepSeek**
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("⚠️ DEEPSEEK_API_KEY is missing. Make sure it's in the .env file!")

    # **Define the DeepSeek model using ChatOpenAI**
    llm = ChatOpenAI(
        temperature=0,
        model_name="deepseek-chat",  # DeepSeek model
        openai_api_base="https://api.deepseek.com/v1",  # Correct API base for DeepSeek
        openai_api_key=api_key  # Use DeepSeek API key
    )

    # **Define a prompt template for the AI model**
    template = """Given the full name {name_of_person}, find the URL to their LinkedIn profile page.
Your answer should contain only the URL."""

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["name_of_person"]
    )

    # **Define Tavily as a search tool for the agent**
    tools_for_agent = [
        Tool(
            name="Search LinkedIn Profile",
            func=get_profile_url_tavily,
            description="Searches for a LinkedIn profile URL based on a person's full name."
        )
    ]

    # **Fetch a predefined ReAct prompt from LangChain Hub**
    react_prompt = hub.pull("hwchase17/react")

    # **Create an AI-powered agent using the ReAct framework**
    agent = create_react_agent(
        llm=llm,
        tools=tools_for_agent,
        prompt=react_prompt
    )

    # **Define an agent executor that will run the agent with the given tools**
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_for_agent,
        verbose=True  # Enables logging of agent's decision-making
    )

    # **Run the agent to retrieve the LinkedIn profile URL**
    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(name_of_person=name)}  # Formats the query with the given name
    )

    # **Extract the LinkedIn profile URL from the agent's response**
    linked_profile_url = result["output"]

    return linked_profile_url  # Return the extracted LinkedIn profile URL


# **Execute when the script runs directly**
if __name__ == "__main__":
    # **Call lookup function and print the result**
    print(lookup(name="Eden Marco"))