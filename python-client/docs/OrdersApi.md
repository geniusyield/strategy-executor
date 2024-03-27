# swagger_client.OrdersApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**v0_orders_delete**](OrdersApi.md#v0_orders_delete) | **DELETE** /v0/orders | Cancel order(s)
[**v0_orders_post**](OrdersApi.md#v0_orders_post) | **POST** /v0/orders | Create an order
[**v0_orders_tx_build_cancel_post**](OrdersApi.md#v0_orders_tx_build_cancel_post) | **POST** /v0/orders/tx/build-cancel | Build transaction to cancel order(s)
[**v0_orders_tx_build_open_post**](OrdersApi.md#v0_orders_tx_build_open_post) | **POST** /v0/orders/tx/build-open | Build transaction to create order


# **v0_orders_delete**
> CancelOrderTransactionDetails v0_orders_delete(body)

Cancel order(s)

Cancel order(s). This endpoint would also sign & submit the built transaction

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
api_instance = swagger_client.OrdersApi(swagger_client.ApiClient(configuration))
body = swagger_client.CancelOrderParameters() # CancelOrderParameters | 

try:
    # Cancel order(s)
    api_response = api_instance.v0_orders_delete(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrdersApi->v0_orders_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CancelOrderParameters**](CancelOrderParameters.md)|  | 

### Return type

[**CancelOrderTransactionDetails**](CancelOrderTransactionDetails.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v0_orders_post**
> PlaceOrderTransactionDetails v0_orders_post(body)

Create an order

Create an order. This endpoint would also sign & submit the built transaction. Order is placed at a mangled address where staking credential is that of the given \"address\" field.

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
api_instance = swagger_client.OrdersApi(swagger_client.ApiClient(configuration))
body = swagger_client.PlaceOrderParameters() # PlaceOrderParameters | 

try:
    # Create an order
    api_response = api_instance.v0_orders_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrdersApi->v0_orders_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PlaceOrderParameters**](PlaceOrderParameters.md)|  | 

### Return type

[**PlaceOrderTransactionDetails**](PlaceOrderTransactionDetails.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v0_orders_tx_build_cancel_post**
> CancelOrderTransactionDetails v0_orders_tx_build_cancel_post(body)

Build transaction to cancel order(s)

Build a transaction to cancel order(s)

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
api_instance = swagger_client.OrdersApi(swagger_client.ApiClient(configuration))
body = swagger_client.CancelOrderParameters() # CancelOrderParameters | 

try:
    # Build transaction to cancel order(s)
    api_response = api_instance.v0_orders_tx_build_cancel_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrdersApi->v0_orders_tx_build_cancel_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CancelOrderParameters**](CancelOrderParameters.md)|  | 

### Return type

[**CancelOrderTransactionDetails**](CancelOrderTransactionDetails.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **v0_orders_tx_build_open_post**
> PlaceOrderTransactionDetails v0_orders_tx_build_open_post(body)

Build transaction to create order

Build a transaction to create an order. Order is placed at a mangled address where staking credential is that of the given \"address\" field.

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
api_instance = swagger_client.OrdersApi(swagger_client.ApiClient(configuration))
body = swagger_client.PlaceOrderParameters() # PlaceOrderParameters | 

try:
    # Build transaction to create order
    api_response = api_instance.v0_orders_tx_build_open_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrdersApi->v0_orders_tx_build_open_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PlaceOrderParameters**](PlaceOrderParameters.md)|  | 

### Return type

[**PlaceOrderTransactionDetails**](PlaceOrderTransactionDetails.md)

### Authorization

[api-key](../README.md#api-key)

### HTTP request headers

 - **Content-Type**: application/json;charset=utf-8
 - **Accept**: application/json;charset=utf-8

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

