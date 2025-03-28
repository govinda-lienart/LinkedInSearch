import os
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Tuple
from output_parsers import summary_parser, Summary
from third_parties.linkedIn import scrape_linkedin_profile
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent


def ice_break_with(name: str) -> Summary:  # ✅ Returns only Summary object
    linkedin_username = linkedin_lookup_agent(name=name)

    linkedin_data = scrape_linkedin_profile(
        linkedin_profile_url=linkedin_username, mock=False  # ✅ Use real data
    )

    print(f"DEBUG: LinkedIn Data: {linkedin_data}")  # ✅ Log LinkedIn Data

    if not linkedin_data:
        print("⚠️ Failed to fetch LinkedIn data. Returning empty results.")
        return Summary(summary="No LinkedIn data found.", facts=[])

    summary_template = """
    Given the LinkedIn information {information} about a person, create:
    1. A short summary
    2. Two interesting facts about them 

    Use only information from LinkedIn.
    \n{format_instructions}
    """
    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=summary_template,
        partial_variables={
            "format_instructions": summary_parser.get_format_instructions()
        },
    )

    # Retrieve API key for DeepSeek
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("⚠️ WARNING: Missing DEEPSEEK_API_KEY. The API might not function correctly.")

    # Initialize the DeepSeek model
    llm = ChatOpenAI(
        temperature=0,
        model_name="deepseek-chat",
        openai_api_base="https://api.deepseek.com/v1",
        openai_api_key=api_key
    )

    chain = summary_prompt_template | llm | summary_parser

    try:
        res: Summary = chain.invoke(input={"information": linkedin_data})
        print(f"DEBUG: Generated Summary: {res.summary}")  # ✅ Debugging output
        print(f"DEBUG: Generated Facts: {res.facts}")  # ✅ Debugging output
        return res  # ✅ Returns only Summary object
    except Exception as e:
        print("ERROR: Issue during summary generation:", str(e))
        return Summary(summary="Error generating summary.", facts=[])


if __name__ == "__main__":
    load_dotenv()
    print("Ice Breaker Enter")
    test_result = ice_break_with(name="Harrison Chase")
    print(test_result.summary)
    print(test_result.facts)