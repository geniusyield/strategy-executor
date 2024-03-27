# swagger_client.OrderBookApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_order_book_market_id_get**](OrderBookApi.md#v0_order_book_market_id_get) | **GET** /v0/order-book/{market-id} | Order book


# **v0_order_book_market_id_get**
> OrderBookInfo v0_order_book_market_id_get(market_id, address=address)

Order book

Get order book for a specific market.

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
api_instance = swagger_client.OrderBookApi(swagger_client.ApiClient(configuration))
market_id = 'market_id_example' # str | 
address = 'address_example' # str |  (optional)

try:
    # Order book
    api_response = api_instance.v0_order_book_market_id_get(market_id, address=address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrderBookApi->v0_order_book_market_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **market_id** | **str**|  | 
 **address** | **str**|  | [optional] 

### Return type

[**OrderBookInfo**](OrderBookInfo.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

