import requests
import json
import os
from langchain.chains import LLMMathChain
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import Tool, tool
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
BASE_URL_SUBWAY = 'http://swopenAPI.seoul.go.kr/api/subway'
BASE_URL_AIR = 'http://openAPI.seoul.go.kr:8088'

from config import DATA_API_KEY# BASE_URL_AIR

def test():
    print('test')
@tool
def get_realtime_city_air(Gu_code=' '):
    """fetches real time air quality by Gu.
    - Gu_code (str): the code of Gu in in Seoul. If it use ' ', the results of all 25 Gu will be returned.
    """
    endpoint = f'{BASE_URL_AIR}/{DATA_API_KEY}/json/ListAirQualityByDistrictService/1/25/{str(Gu_code)}/'#{region}'
    print(endpoint)
    response = requests.get(endpoint)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return 'Error fetching real-time city air status'

@tool
def get_seoul_market_prices( market_name="이마트", item_name="사과", year_month= " ", start_index=1, end_index=15, request_type='json'):

    """
    Fetches price information for specified market and item for a given time period from the Seoul City API.

    Parameters:
    - market_name (str): Name of the market (e.g., "롯데마트 서울역점").
    - item_name (str): Name of the item (e.g., "사과").It has to be written in Korean.
    - year_month (str): The year and month of interest in "YYYY-MM" format.
    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).
    - request_type (str): Type of the response requested (xml, xls, json; default is json).

    Returns:
    dict: Parsed JSON response from the API if request_type is 'json'; raw response otherwise.
    """
    # Constructing the URL based on the function parameters
    url = f"http://openAPI.seoul.go.kr:8088/{DATA_API_KEY}/{request_type}/ListNecessariesPricesService/{start_index}/{end_index}/{market_name}/{item_name}/{year_month}/"
    print(url)
    # Making the API request
    response = requests.get(url)

    # Check if request_type is 'json' to return a parsed JSON; otherwise, return text
    if request_type == 'json' and response.status_code == 200:
        return response.json()
    else:
        return response.text
@tool
def get_api_base_info( api_code=' ',api_keyword=' ', start_index=1, end_index=5, request_type='json'):
    """
    Fetches API mata data from the Seoul Open Data Plaza.

    Parameters:
    - api_code (str):api code in the system, such as OA-1200
    - api_keyword (str): The keyword to serearch related API by name. It has to be written in Korean.

    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).
    - request_type (str): Type of the response requested (xml, xls, json; default is json).

    Returns:
    dict: Parsed JSON response from the API if request_type is 'json'; raw response otherwise.
    """
    # Constructing the URL based on the function parameters
    url = f"http://openAPI.seoul.go.kr:8088/{DATA_API_KEY}/{request_type}/SearchCatalogService/{start_index}/{end_index}/{api_code}/{api_keyword}/"
    print(url)
    # Making the API request
    response = requests.get(url)

    # Check if request_type is 'json' to return a parsed JSON; otherwise, return text
    if request_type == 'json' and response.status_code == 200:
        return response.json()
    else:
        return response.text
@tool
def get_bike_rental_info(start_index=1, end_index=5, request_type='json', station_id=''):
    """
    Fetches real-time rental information for public bicycles in Seoul.

    Parameters:
    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).
    - request_type (str): Type of the response requested (xml, xls, json; default is json).
    - station_id (str): The specific station ID for which information is requested. Leave blank for general data.

    Returns:
    dict or str: Parsed JSON response from the API if request_type is 'json'; raw response otherwise.
    """
    # Constructing the URL based on the function parameters
    url = f"http://openAPI.seoul.go.kr:8088/{DATA_API_KEY}/{request_type}/bikeList/{start_index}/{end_index}/{station_id}"
    print(url)
    # Making the API request
    response = requests.get(url)

    # Check if request_type is 'json' to return a parsed JSON; otherwise, return text
    if request_type == 'json' and response.status_code == 200:
        return response.json()
    else:
        return response.text
@tool
def get_city_population( area_name, start_index=1, end_index=5,response_format='json'):
    """
    Fetches real-time and expected population data for specific hotspots in Seoul from the Seoul Open API. It can give travel suggestions about crowdedness.

    Parameters:

    - area_name (str): Name of the hotspot area in Korean (e.g., "광화문·덕수궁, 여의도,잠실").
    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).



    """
    # Constructing the URL based on the function parameters
    url = f"http://openapi.seoul.go.kr:8088/{DATA_API_KEY}/{response_format}/citydata_ppltn/{start_index}/{end_index}/{area_name}/"

    # Making the API request
    response = requests.get(url)

    # Check the status of the response
    if response.status_code == 200:
        if response_format == 'json':
            return response.json()  # Return JSON object if response_format is json
        else:
            return response.text  # Return raw XML string otherwise
    else:
        return f"Error fetching data: {response.status_code}"