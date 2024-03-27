# swagger_client.HistoricalPricesApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_historical_prices_maestro_market_id_dex_get**](HistoricalPricesApi.md#v0_historical_prices_maestro_market_id_dex_get) | **GET** /v0/historical-prices/maestro/{market-id}/{dex} | Get price history using Maestro.


# **v0_historical_prices_maestro_market_id_dex_get**
> list[MarketOHLC] v0_historical_prices_maestro_market_id_dex_get(market_id, dex, resolution=resolution, _from=_from, to=to, limit=limit, sort=sort)

Get price history using Maestro.

This endpoint internally calls Maestro's \"DEX And Pair OHLC\" endpoint.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: api-key
configuration = swagger_client.Configuration()
configuration.api_key['api-key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api-key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.HistoricalPricesApi(swagger_client.ApiClient(configuration))
market_id = 'market_id_example' # str | 
dex = 'dex_example' # str | 
resolution = 'resolution_example' # str |  (optional)
_from = '2013-10-20' # date |  (optional)
to = '2013-10-20' # date |  (optional)
limit = 56 # int |  (optional)
sort = 'sort_example' # str |  (optional)

try:
    # Get price history using Maestro.
    api_response = api_instance.v0_historical_prices_maestro_market_id_dex_get(market_id, dex, resolution=resolution, _from=_from, to=to, limit=limit, sort=sort)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling HistoricalPricesApi->v0_historical_prices_maestro_market_id_dex_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **market_id** | **str**|  | 
 **dex** | **str**|  | 
 **resolution** | **str**|  | [optional] 
 **_from** | **date**|  | [optional] 
 **to** | **date**|  | [optional] 
 **limit** | **int**|  | [optional] 
 **sort** | **str**|  | [optional] 

### Return type

[**list[MarketOHLC]**](MarketOHLC.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

