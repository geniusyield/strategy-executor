# swagger_client.BalancesApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_balances_address_get**](BalancesApi.md#v0_balances_address_get) | **GET** /v0/balances/{address} | Balances


# **v0_balances_address_get**
> GYValue v0_balances_address_get(address)

Balances

Get token balances of an address.

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
api_instance = swagger_client.BalancesApi(swagger_client.ApiClient(configuration))
address = 'address_example' # str | 

try:
    # Balances
    api_response = api_instance.v0_balances_address_get(address)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BalancesApi->v0_balances_address_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **address** | **str**|  | 

### Return type

[**GYValue**](GYValue.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

