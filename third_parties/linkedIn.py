import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def scrape_linkedin_profile(linkedin_profile_url: str, mock: bool = True):
    """Scrape information from LinkedIn profiles, manually scrape the information from the LinkedIn profile"""

    if mock:
        linkedin_profile_url = "https://gist.githubusercontent.com/govinda-lienart/78c49ecaffcc77b61db1568abea39761/raw/491b6640cbdb95a192992a0e3d7f1258edef6eca/eden-marco-scrapin.json"
        response = requests.get(
            linkedin_profile_url,
            timeout=10,
        )
    else:
        api_endpoint = "https://api.scrapin.io/enrichment/profile"
        params = {
            "apikey": os.environ["SCRAPIN_API_KEY"],
            "linkedInUrl": linkedin_profile_url,
        }
        response = requests.get(
            api_endpoint,
            params=params,
            timeout=10,
        )

    # ✅ Set a breakpoint here for Evaluate Expression
    data = response.json().get("person")

    data = {
        k: v
        for k, v in data.items()
        if v not in ([], "", "", None) and k not in ["certifications"]
    }

    return data

if __name__ == "__main__":
    print(
        scrape_linkedin_profile(
            linkedin_profile_url="https://www.linkedin.com/in/eden-marco/", mock=True
        ),
    )