# coding: utf-8

"""
    Genius Yield DEX Server API

    API to interact with GeniusYield DEX.  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import unittest

import swagger_client
from swagger_client.api.order_book_api import OrderBookApi  # noqa: E501
from swagger_client.rest import ApiException


class TestOrderBookApi(unittest.TestCase):
    """OrderBookApi unit test stubs"""

    def setUp(self):
        self.api = swagger_client.api.order_book_api.OrderBookApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_v0_order_book_market_id_get(self):
        """Test case for v0_order_book_market_id_get

        Order book  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
