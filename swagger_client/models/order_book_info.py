# coding: utf-8

"""
    Genius Yield DEX Server API

    API to interact with GeniusYield DEX.  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from swagger_client.configuration import Configuration


class OrderBookInfo(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'asks': 'list[OrderInfo]',
        'bids': 'list[OrderInfo]',
        'market_pair_id': 'OrderAssetPair',
        'timestamp': 'str'
    }

    attribute_map = {
        'asks': 'asks',
        'bids': 'bids',
        'market_pair_id': 'market_pair_id',
        'timestamp': 'timestamp'
    }

    def __init__(self, asks=None, bids=None, market_pair_id=None, timestamp=None, _configuration=None):  # noqa: E501
        """OrderBookInfo - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._asks = None
        self._bids = None
        self._market_pair_id = None
        self._timestamp = None
        self.discriminator = None

        self.asks = asks
        self.bids = bids
        self.market_pair_id = market_pair_id
        self.timestamp = timestamp

    @property
    def asks(self):
        """Gets the asks of this OrderBookInfo.  # noqa: E501


        :return: The asks of this OrderBookInfo.  # noqa: E501
        :rtype: list[OrderInfo]
        """
        return self._asks

    @asks.setter
    def asks(self, asks):
        """Sets the asks of this OrderBookInfo.


        :param asks: The asks of this OrderBookInfo.  # noqa: E501
        :type: list[OrderInfo]
        """
        if self._configuration.client_side_validation and asks is None:
            raise ValueError("Invalid value for `asks`, must not be `None`")  # noqa: E501

        self._asks = asks

    @property
    def bids(self):
        """Gets the bids of this OrderBookInfo.  # noqa: E501


        :return: The bids of this OrderBookInfo.  # noqa: E501
        :rtype: list[OrderInfo]
        """
        return self._bids

    @bids.setter
    def bids(self, bids):
        """Sets the bids of this OrderBookInfo.


        :param bids: The bids of this OrderBookInfo.  # noqa: E501
        :type: list[OrderInfo]
        """
        if self._configuration.client_side_validation and bids is None:
            raise ValueError("Invalid value for `bids`, must not be `None`")  # noqa: E501

        self._bids = bids

    @property
    def market_pair_id(self):
        """Gets the market_pair_id of this OrderBookInfo.  # noqa: E501


        :return: The market_pair_id of this OrderBookInfo.  # noqa: E501
        :rtype: OrderAssetPair
        """
        return self._market_pair_id

    @market_pair_id.setter
    def market_pair_id(self, market_pair_id):
        """Sets the market_pair_id of this OrderBookInfo.


        :param market_pair_id: The market_pair_id of this OrderBookInfo.  # noqa: E501
        :type: OrderAssetPair
        """
        if self._configuration.client_side_validation and market_pair_id is None:
            raise ValueError("Invalid value for `market_pair_id`, must not be `None`")  # noqa: E501

        self._market_pair_id = market_pair_id

    @property
    def timestamp(self):
        """Gets the timestamp of this OrderBookInfo.  # noqa: E501

        This is the posix time in ISO8601 format.  # noqa: E501

        :return: The timestamp of this OrderBookInfo.  # noqa: E501
        :rtype: str
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this OrderBookInfo.

        This is the posix time in ISO8601 format.  # noqa: E501

        :param timestamp: The timestamp of this OrderBookInfo.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and timestamp is None:
            raise ValueError("Invalid value for `timestamp`, must not be `None`")  # noqa: E501

        self._timestamp = timestamp

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(OrderBookInfo, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, OrderBookInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OrderBookInfo):
            return True

        return self.to_dict() != other.to_dict()