from langchain_core.tools import tool

from langchain_community.tools import TavilySearchResults

from . import fourSquareTool
from . import amadeusFlightTool

# @tool
# def add(a: int, b: int):
#     """Add two numbers. Please let the user know that you're adding the numbers BEFORE you call the tool"""
#     return a + b

tavily_tool = TavilySearchResults(
    max_results=5,
    include_answer=True,
    description=(
        "This is a search tool for accessing the internet.\n\n"
        "Let the user know you're asking your friend Tavily for help before you call the tool."
    ),
)

four_square_tools = [
    fourSquareTool.search_near,
    fourSquareTool.search_near_point,
    fourSquareTool.place_snap,
    fourSquareTool.place_details,
    fourSquareTool.get_location
]

amadeus_flight_tools = [
    amadeusFlightTool.flight_offers_search,
    amadeusFlightTool.flight_offers_price,
    amadeusFlightTool.flight_create_order
]

TOOLS = [tavily_tool, *four_square_tools, *amadeus_flight_tools]
