from tools import seoul_api

# This test if the tools for fetching API works
# Tools are saved in tools.seoul_api.py


area_name = "여의도"
print(seoul_api.get_city_population( area_name))


# Fetch real-time city air quality
air_quality = seoul_api.get_realtime_city_air('11010')
print(air_quality)

# Fetch market prices
market_prices = seoul_api.get_seoul_market_prices({"market_name":'이마트',"item_name":"우유"})

print(market_prices)
