from langchain_core.tools import tool

# tool functions
@tool
def get_weather(location: str) -> str:
    """Get the weather in a given location.
    
    Args:
        location: The city and state/country (e.g., "San Francisco, CA" or "London, UK")
    """
    return f"The weather in {location} is sunny"

