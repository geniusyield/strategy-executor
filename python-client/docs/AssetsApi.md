# swagger_client.AssetsApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_assets_asset_get**](AssetsApi.md#v0_assets_asset_get) | **GET** /v0/assets/{asset} | Get assets information


# **v0_assets_asset_get**
> AssetDetails v0_assets_asset_get(asset)

Get assets information

Get information for a specific asset.

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
api_instance = swagger_client.AssetsApi(swagger_client.ApiClient(configuration))
asset = 'asset_example' # str | 

try:
    # Get assets information
    api_response = api_instance.v0_assets_asset_get(asset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssetsApi->v0_assets_asset_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset** | **str**|  | 

### Return type

[**AssetDetails**](AssetDetails.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

