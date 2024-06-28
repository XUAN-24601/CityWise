# %% [markdown]
# # Plan-and-execute
# 
# Plan-and-execute agents accomplish an objective by first planning what to do, then executing the sub tasks. This idea is largely inspired by [BabyAGI](https://github.com/yoheinakajima/babyagi) and then the ["Plan-and-Solve" paper](https://arxiv.org/abs/2305.04091).
# 
# The planning is almost always done by an LLM.
# 
# The execution is usually done by a separate agent (equipped with tools).

# %%
#直接执行下面的就可以

# %% [markdown]
# ## Imports

# %%
colab=0
if colab:
    from google.colab import drive
    drive.mount('/content/drive')
    !pip install langchain-experimental
    ! pip install openai
    ! pip install levenshtein
    ! pip install langchain
    !pip install thefuzz

# %%
from langchain.chains import LLMMathChain
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
#from langchain_openai import ChatOpenAI, OpenAI

# %% [markdown]
# ## Tools

# %%
#! pip install wikipedia
'''
import wikipedia

@tool
def search(query: str) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 3]:
        try:
            wiki_page =  wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}")
        except (
            self.wiki_client.exceptions.PageError,
            self.wiki_client.exceptions.DisambiguationError,
        ):
            pass
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)
#search = DuckDuckGoSearchAPIWrapper()
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model=GPT_MODEL)#OpenAI(temperature=0)
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    ),
]
model = ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,model=GPT_MODEL)
planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor)
agent.run(
    "Who is the current prime minister of the UK? What is their current age raised to the 0.43 power?"
)'''

# %%
from langchain.tools import tool
from langchain.chat_models import ChatOpenAI

# %%
OPENAI_API_KEY= 'sk-xxxxxxxxxxxxxxxxxxxxxx'
GPT_MODEL = "gpt-3.5-turbo-0613"

# %% [markdown]
# ## Planner, Executor, and Agent
# 

# %% [markdown]
# ## Run example

# %%
from thefuzz import process
import json
import pandas as pd
from json import loads, dumps

# Define the path to your JSON file
file_path = '/content/drive/MyDrive/citywise/Public_bike_station_code.json' ##TODO change the path and load the id filr

# Load the JSON content from the file into a dictionary
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        station_code_dict = json.load(file)
    print("JSON data loaded successfully!")
except Exception as e:
    print(f"Error loading JSON data: {e}")
bike_station_code_dict=station_code_dict['DATA']

main_AOI_code= json.loads(pd.read_csv('/content/drive/MyDrive/citywise/115 service locations code list.csv').to_json(orient="records")
)


# %%

from thefuzz import process
@tool
def find_possible_ids_by_fuzzy_query(query_address, code_name='bike stations', ):
    """
    Searches for and returns IDs that closely match a given query, such as addresses or names, using fuzzy string matching. This function is versatile and can be applied to different datasets by specifying the `code_type`. It's particularly useful for scenarios where an exact match for an address or name cannot be found, enabling the user to retrieve the most relevant IDs based on similarity scores.

    Parameters:
    - query_address (str): The address or name query to match against. This could be an address for a bike station or a name for an area of interest (AOI).
    - code_name (str): Specifies the type of data to query against. Defaults to 'bike stations'. Other supported types could be 'AOI', each referring to a specific dataset.
    - limit (int): The maximum number of top matches to return, based on their similarity to the query. Defaults to 3.

    Returns:
    List of tuples: Each tuple contains the matched string, its corresponding ID, and the similarity score. The list is sorted by the similarity score in descending order. If no matches are found above a specified threshold, the function may return an empty list.

    Explanation:
    The function first constructs a dictionary mapping addresses or names to their corresponding IDs based on the specified `code_type`. For bike stations, the dictionary keys are concatenated strings of station addresses, while for AOI, they are concatenated strings of area names in both Korean and English. It then uses fuzzy string matching to find the top `N` matches between the query and the keys of this dictionary. The similarity score is calculated, and matches are returned along with their corresponding IDs and scores, allowing the user to identify the most relevant IDs for further processing or querying.
    """
    ...
    # Combine statn_addr1 and statn_addr2 for full addresses, map to lendplace_id
    if code_name=='bike stations':
      address_to_id = {f"{station['statn_addr1']}, {station['statn_addr2']}": station['lendplace_id'] for station in bike_station_code_dict}


    if code_name=='AOI':
      address_to_id={f"{AOI['AREA_NM']}, {AOI['ENG_NM']}": AOI['AREA_CD'] for AOI in main_AOI_code}#pd.concat([main_AOI_code['AREA_NM'],main_AOI_code['ENG_NM']]).reset_index(drop=True)
    # Find the best match for the query address
    top_matches = process.extract(query_address, address_to_id.keys(), limit=3)
    print(top_matches)
    # Map the matches back to their station IDs and include match scores
    top_station_ids_with_scores = [(match[0],address_to_id[match[0]], match[1]) for match in top_matches]

    return top_station_ids_with_scores
query_address = "Gangnam"  # An example partial or slightly incorrect address

##station_id = find_possible_ids_by_fuzzy_query(query_address,code_name='bike stations' )
#station_id

# %% [markdown]
# ## start citywise

# %%
@tool
def get_bike_rental_info(start_index=1, end_index=5, request_type='json', station_id=''):
    """
    Fetches real-time rental information for public bicycles in Seoul by station ID, including . Bedore using this function, it requires fetches ID by function find_possible_ids_by_fuzzy_query.

    Parameters:
    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).
    - request_type (str): Type of the response requested (xml, xls, json; default is json).
    - station_id (str): The specific station ID for which information is requested. Leave blank for general data.

    Returns:
    dict or str: Parsed JSON response from the API if request_type is 'json'; raw response otherwise.
    Real-time bike availability and pickup rates by stations.
    """
    # Constructing the URL based on the function parameters
    url = f"http://openAPI.seoul.go.kr:8088/{API_KEY}/{request_type}/bikeList/{start_index}/{end_index}/{station_id}"
    print(url)
    # Making the API request
    response = requests.get(url)

    # Check if request_type is 'json' to return a parsed JSON; otherwise, return text
    if request_type == 'json' and response.status_code == 200:
        return response.json()
    else:
        return response.text

# %% [markdown]
# #functions

# %%
import requests
import json

API_KEY ="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Replace with your actual API key
BASE_URL_SUBWAY = 'http://swopenAPI.seoul.go.kr/api/subway'
BASE_URL_AIR = 'http://openAPI.seoul.go.kr:8088'

@tool
def get_realtime_city_air(Gu_code=' '):
    """fetches real time air quality by Gu.
    - Gu_code (str): the code of Gu in in Seoul. If it use ' ', the results of all 25 Gu will be returned.
    """
    endpoint = f'{BASE_URL_AIR}/{API_KEY}/json/ListAirQualityByDistrictService/1/25/{str(Gu_code)}/'#{region}'
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
    - key (str): Your API key.
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
    url = f"http://openAPI.seoul.go.kr:8088/{API_KEY}/{request_type}/ListNecessariesPricesService/{start_index}/{end_index}/{market_name}/{item_name}/{year_month}/"
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
    url = f"http://openAPI.seoul.go.kr:8088/{API_KEY}/{request_type}/SearchCatalogService/{start_index}/{end_index}/{api_code}/{api_keyword}/"
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
    url = f"http://openAPI.seoul.go.kr:8088/{API_KEY}/{request_type}/bikeList/{start_index}/{end_index}/{station_id}"
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
    - if_test (bool): if print the complied url for testing


    """
    # Constructing the URL based on the function parameters
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/{response_format}/citydata_ppltn/{start_index}/{end_index}/{area_name}/"

    # Making the API request
    response = requests.get(url)

    if if_test:
        print(url)
    # Check the status of the response
    if response.status_code == 200:
        if response_format == 'json':
            return response.json()  # Return JSON object if response_format is json
        else:
            return response.text  # Return raw XML string otherwise
    else:
        return f"Error fetching data: {response.status_code}"

@tool
def get_city_population_eng( area_name, start_index=1, end_index=5,response_format='json'):
    """
    Fetches real-time and expected population data for specific hotspots in Seoul from the Seoul Open API. It can give travel suggestions about crowdedness.

    Parameters:

    - area_name (str): Name of the hotspot area in Korean (e.g., "광화문·덕수궁, 여의도,잠실").
    - start_index (int): Starting index for paging (default is 1).
    - end_index (int): Ending index for paging (default is 5).



    """
    # Constructing the URL based on the function parameters
    url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/{response_format}/citydata_ppltn/{start_index}/{end_index}/{area_name}/"
    if if_test:
        print(url)
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
# Example usage:
if_test=True
area_name = "여의도"#"Yeouido"
print(get_city_population( area_name))


# %%
tools=[ get_realtime_city_air,get_api_base_info,get_seoul_market_prices, get_bike_rental_info,  find_possible_ids_by_fuzzy_query,get_city_population,]

# %%
tools[0]

# %%
model = ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,model=GPT_MODEL)
planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

# %%
questions=["which area has better air quality, 종로구 or 강동구? ","What data API do you have about bikes?","Which fruit is cheaper? Apple of pear?",'Is there any bike left near Gangnam? ','I want to go to Yeouido. Is it crowded in 2 hours?']

# %%
import sys

# %%
%%time
%%capture cap


##    Your Code    ##

agent.invoke(questions[-1]

)



# %% [markdown]
# ## Output experiment

# %%
f = open("output.txt", "w")
print(cap, file=f)
f.close()


