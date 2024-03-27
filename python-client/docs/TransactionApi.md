# swagger_client.TransactionApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_tx_sign_and_submit_post**](TransactionApi.md#v0_tx_sign_and_submit_post) | **POST** /v0/tx/sign-and-submit | Sign and submit a transaction
[**v0_tx_sign_post**](TransactionApi.md#v0_tx_sign_post) | **POST** /v0/tx/sign | Sign a transaction
[**v0_tx_submit_post**](TransactionApi.md#v0_tx_submit_post) | **POST** /v0/tx/submit | Submit a transaction


# **v0_tx_sign_and_submit_post**
> GYTxId v0_tx_sign_and_submit_post(body)

Sign and submit a transaction

Signs the given transaction using key configured in server and submits it to the network.

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
api_instance = swagger_client.TransactionApi(swagger_client.ApiClient(configuration))
body = swagger_client.GYTx() # GYTx | 

try:
    # Sign and submit a transaction
    api_response = api_instance.v0_tx_sign_and_submit_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TransactionApi->v0_tx_sign_and_submit_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**GYTx**](GYTx.md)|  | 

### Return type

[**GYTxId**](GYTxId.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v0_tx_sign_post**
> GYTx v0_tx_sign_post(body)

Sign a transaction

Signs the given transaction using key configured in server.

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
api_instance = swagger_client.TransactionApi(swagger_client.ApiClient(configuration))
body = swagger_client.GYTx() # GYTx | 

try:
    # Sign a transaction
    api_response = api_instance.v0_tx_sign_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TransactionApi->v0_tx_sign_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**GYTx**](GYTx.md)|  | 

### Return type

[**GYTx**](GYTx.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v0_tx_submit_post**
> GYTxId v0_tx_submit_post(body)

Submit a transaction

Submits the given transaction to the network.

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
api_instance = swagger_client.TransactionApi(swagger_client.ApiClient(configuration))
body = swagger_client.GYTx() # GYTx | 

try:
    # Submit a transaction
    api_response = api_instance.v0_tx_submit_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TransactionApi->v0_tx_submit_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**GYTx**](GYTx.md)|  | 

### Return type

[**GYTxId**](GYTxId.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

