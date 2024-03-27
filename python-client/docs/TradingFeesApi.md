# swagger_client.TradingFeesApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_trading_fees_get**](TradingFeesApi.md#v0_trading_fees_get) | **GET** /v0/trading-fees | Trading fees


# **v0_trading_fees_get**
> TradingFees v0_trading_fees_get()

Trading fees

Get trading fees of DEX.

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
api_instance = swagger_client.TradingFeesApi(swagger_client.ApiClient(configuration))

try:
    # Trading fees
    api_response = api_instance.v0_trading_fees_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TradingFeesApi->v0_trading_fees_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TradingFees**](TradingFees.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

