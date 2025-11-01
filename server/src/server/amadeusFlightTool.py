from langchain_core.tools import tool

import os
import json
# from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests

# mcp = FastMCP(
#     name="Amadeus MCP",
#     host="0.0.0.0",  # only used for SSE transport (localhost)
#     port=8050,  # only used for SSE transport (set this to any port)
# )

# Load environment variables
load_dotenv(".env")

@tool()
def flight_offers_search(
    originLocationCode: str,
    destinationLocationCode: str,
    departureDate: str,
    returnDate: str = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    travelClass: str = None,
    includedAirlineCodes: str = None,
    excludedAirlineCodes: str = None,
    nonStop: bool = False,
    currencyCode: str = None,
    maxPrice: int = None,
    max: int = 250
) -> str:
    """Return list of Flight Offers based on searching criteria.
    Make reasonable assumptions if some parameters are missing. Don't ask the user for them.
    If there is no date mentione, use todays date.
    Make sure to take todays date accurately into account when making assumptions.
    Make reasonable assumptions about the nearest airport with the given location.
    If the location is a city, use the main airport for that city.

    travelClass: string (optional)
    Accepted values: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST.
    If not specified, any travel class is considered.

    includedAirlineCodes: string (optional)
        Only consider these airlines. Cannot be used with excludedAirlineCodes.
        Airlines are specified as IATA codes, comma-separated (e.g. '6X,7X,8X').

    excludedAirlineCodes: string (optional)
        Ignore these airlines. Cannot be used with includedAirlineCodes.
        Airlines are specified as IATA codes, comma-separated (e.g. '6X,7X,8X').
    
    nonStop: boolean (optional)
        If true, only return nonstop flights. Default is false.
    
    maxPrice: integer (optional)
        The maximum price of the flight offers to be returned.
    
    max: integer (optional)
        The maximum number of flight offers to be returned. Default is 250.
    
    currencyCode: string (optional)
        Currency code, in ISO 4217 format. If not specified, defaults to EUR.
    
    """
    try:
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"  # Replace with your real API endpoint
        params = {
            "originLocationCode": originLocationCode,
            "destinationLocationCode": destinationLocationCode,
            "departureDate": departureDate,
            "adults": adults,
            "max": max,
        }
        # Add optional parameters if provided
        if returnDate: params["returnDate"] = returnDate
        if children: params["children"] = children
        if infants: params["infants"] = infants
        if travelClass: params["travelClass"] = travelClass
        if includedAirlineCodes: params["includedAirlineCodes"] = includedAirlineCodes
        if excludedAirlineCodes: params["excludedAirlineCodes"] = excludedAirlineCodes
        if currencyCode: params["currencyCode"] = currencyCode
        if maxPrice: params["maxPrice"] = maxPrice
        if nonStop: params["nonStop"] = nonStop

        # Add authentication headers if needed
        headers = {"Authorization": f"Bearer {os.getenv('AMADEUS_API_KEY')}"}
        print(headers)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.RequestException as e:
        return json.dumps({"error": f"Request error: {str(e)}"})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"error": f"Error fetching flight schedule: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
@tool()
def flight_offers_price(
    priceFlightOffersBody: dict,
    include: str = None,
    forceClass: bool = False
) -> str:
    """
    Confirm pricing of given flightOffers.
    Makes a POST request to /shopping/flight-offers/pricing.

    priceFlightOffersBody: dict (required)
        The request body matching Amadeus flight-offers-pricing spec.
    include: string (optional)
        Comma-separated sub-resources to include (credit-card-fees, bags, other-services, detailed-fare-rules).
    forceClass: boolean (optional)
        True to force pricing with the specified booking class, false for best available price.
    """
    try:
        url = "https://test.api.amadeus.com/v1/shopping/flight-offers/pricing"
        headers = {
            "Authorization": f"Bearer {os.getenv('AMADEUS_API_KEY')}",
            "Content-Type": "application/vnd.amadeus+json",
            "X-HTTP-Method-Override": "GET"
        }
        params = {}
        if include:
            params["include"] = include
        params["forceClass"] = str(forceClass).lower()
        response = requests.post(
            url,
            params=params,
            headers=headers,
            data=json.dumps(priceFlightOffersBody),
            timeout=15
        )
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.RequestException as e:
        return json.dumps({"error": f"Request error: {str(e)}"})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"error": f"Error fetching flight pricing: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
@tool()
def flight_create_order(
    body: dict
) -> str:
    """
    Create a flight order associated to the flight offers.
    Makes a POST request to /booking/flight-orders.

    body: dict (required)
        The request body must match the Amadeus flight-order spec and include ALL mandatory fields:
        {
            "data": {
                "type": "flight-order",
                "flightOffers": [ ... ],  # confirmed flight offer(s)
                "travelers": [
                    {
                        "id": "1",
                        "dateOfBirth": "YYYY-MM-DD",
                        "name": {"firstName": "...", "lastName": "..."},
                        "gender": "MALE"|"FEMALE",
                        "contact": {"emailAddress": "...", "phones": [...]},
                        "documents": [
                            {
                                "documentType": "PASSPORT",
                                "birthPlace": "...",
                                "issuanceLocation": "...",
                                "issuanceDate": "YYYY-MM-DD",
                                "number": "...",
                                "expiryDate": "YYYY-MM-DD",           # REQUIRED
                                "issuanceCountry": "...",             # REQUIRED
                                "validityCountry": "...",
                                "nationality": "...",                 # REQUIRED
                                "holder": true|false                    # REQUIRED
                            }
                        ]
                    }
                ],
                "contacts": [
                    {
                        "addresseeName": {"firstName": "...", "lastName": "..."},
                        "companyName": "...",
                        "purpose": "...",
                        "phones": [...],
                        "emailAddress": "...",
                        "address": {
                            "lines": ["..."],
                            "postalCode": "...",
                            "cityName": "...",
                            "countryCode": "..."                     # REQUIRED
                        }
                    }
                ],
                "remarks": { ... },       # optional
                "ticketingAgreement": { ... },  # optional
            }
        }

    Note: The Amadeus API will return errors if any mandatory field is missing. Do NOT omit required fields such as nationality, expiryDate, issuanceCountry, holder in traveler documents, or address in contacts.
    """
    try:
        url = "https://test.api.amadeus.com/v1/booking/flight-orders"
        headers = {
            "Authorization": f"Bearer {os.getenv('AMADEUS_API_KEY')}",
            "Content-Type": "application/vnd.amadeus+json"
        }
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(body),
            timeout=15
        )
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.RequestException as e:
        return json.dumps({"error": f"Request error: {str(e)}"})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"error": f"Error creating flight order: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
