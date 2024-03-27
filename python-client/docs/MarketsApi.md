# swagger_client.MarketsApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_markets_get**](MarketsApi.md#v0_markets_get) | **GET** /v0/markets | Get markets information for the DEX.


# **v0_markets_get**
> list[Market] v0_markets_get()

Get markets information for the DEX.

Returns the list of markets information supported by GeniusYield DEX.

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
api_instance = swagger_client.MarketsApi(swagger_client.ApiClient(configuration))

try:
    # Get markets information for the DEX.
    api_response = api_instance.v0_markets_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MarketsApi->v0_markets_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Market]**](Market.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

