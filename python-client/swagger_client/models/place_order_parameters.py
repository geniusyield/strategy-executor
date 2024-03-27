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


class PlaceOrderParameters(object):
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
        'address': 'GYAddressBech32',
        'collateral': 'GYTxOutRef',
        'end': 'str',
        'offer_amount': 'GYNatural',
        'offer_token': 'GYAssetClass',
        'price_amount': 'GYNatural',
        'price_token': 'GYAssetClass',
        'start': 'str'
    }

    attribute_map = {
        'address': 'address',
        'collateral': 'collateral',
        'end': 'end',
        'offer_amount': 'offer_amount',
        'offer_token': 'offer_token',
        'price_amount': 'price_amount',
        'price_token': 'price_token',
        'start': 'start'
    }

    def __init__(self, address=None, collateral=None, end=None, offer_amount=None, offer_token=None, price_amount=None, price_token=None, start=None, _configuration=None):  # noqa: E501
        """PlaceOrderParameters - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._address = None
        self._collateral = None
        self._end = None
        self._offer_amount = None
        self._offer_token = None
        self._price_amount = None
        self._price_token = None
        self._start = None
        self.discriminator = None

        self.address = address
        self.collateral = collateral
        if end is not None:
            self.end = end
        self.offer_amount = offer_amount
        self.offer_token = offer_token
        self.price_amount = price_amount
        self.price_token = price_token
        if start is not None:
            self.start = start

    @property
    def address(self):
        """Gets the address of this PlaceOrderParameters.  # noqa: E501


        :return: The address of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYAddressBech32
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this PlaceOrderParameters.


        :param address: The address of this PlaceOrderParameters.  # noqa: E501
        :type: GYAddressBech32
        """
        if self._configuration.client_side_validation and address is None:
            raise ValueError("Invalid value for `address`, must not be `None`")  # noqa: E501

        self._address = address

    @property
    def collateral(self):
        """Gets the collateral of this PlaceOrderParameters.  # noqa: E501


        :return: The collateral of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYTxOutRef
        """
        return self._collateral

    @collateral.setter
    def collateral(self, collateral):
        """Sets the collateral of this PlaceOrderParameters.


        :param collateral: The collateral of this PlaceOrderParameters.  # noqa: E501
        :type: GYTxOutRef
        """
        if self._configuration.client_side_validation and collateral is None:
            raise ValueError("Invalid value for `collateral`, must not be `None`")  # noqa: E501

        self._collateral = collateral

    @property
    def end(self):
        """Gets the end of this PlaceOrderParameters.  # noqa: E501

        This is the posix time in ISO8601 format.  # noqa: E501

        :return: The end of this PlaceOrderParameters.  # noqa: E501
        :rtype: str
        """
        return self._end

    @end.setter
    def end(self, end):
        """Sets the end of this PlaceOrderParameters.

        This is the posix time in ISO8601 format.  # noqa: E501

        :param end: The end of this PlaceOrderParameters.  # noqa: E501
        :type: str
        """

        self._end = end

    @property
    def offer_amount(self):
        """Gets the offer_amount of this PlaceOrderParameters.  # noqa: E501


        :return: The offer_amount of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYNatural
        """
        return self._offer_amount

    @offer_amount.setter
    def offer_amount(self, offer_amount):
        """Sets the offer_amount of this PlaceOrderParameters.


        :param offer_amount: The offer_amount of this PlaceOrderParameters.  # noqa: E501
        :type: GYNatural
        """
        if self._configuration.client_side_validation and offer_amount is None:
            raise ValueError("Invalid value for `offer_amount`, must not be `None`")  # noqa: E501

        self._offer_amount = offer_amount

    @property
    def offer_token(self):
        """Gets the offer_token of this PlaceOrderParameters.  # noqa: E501


        :return: The offer_token of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYAssetClass
        """
        return self._offer_token

    @offer_token.setter
    def offer_token(self, offer_token):
        """Sets the offer_token of this PlaceOrderParameters.


        :param offer_token: The offer_token of this PlaceOrderParameters.  # noqa: E501
        :type: GYAssetClass
        """
        if self._configuration.client_side_validation and offer_token is None:
            raise ValueError("Invalid value for `offer_token`, must not be `None`")  # noqa: E501

        self._offer_token = offer_token

    @property
    def price_amount(self):
        """Gets the price_amount of this PlaceOrderParameters.  # noqa: E501


        :return: The price_amount of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYNatural
        """
        return self._price_amount

    @price_amount.setter
    def price_amount(self, price_amount):
        """Sets the price_amount of this PlaceOrderParameters.


        :param price_amount: The price_amount of this PlaceOrderParameters.  # noqa: E501
        :type: GYNatural
        """
        if self._configuration.client_side_validation and price_amount is None:
            raise ValueError("Invalid value for `price_amount`, must not be `None`")  # noqa: E501

        self._price_amount = price_amount

    @property
    def price_token(self):
        """Gets the price_token of this PlaceOrderParameters.  # noqa: E501


        :return: The price_token of this PlaceOrderParameters.  # noqa: E501
        :rtype: GYAssetClass
        """
        return self._price_token

    @price_token.setter
    def price_token(self, price_token):
        """Sets the price_token of this PlaceOrderParameters.


        :param price_token: The price_token of this PlaceOrderParameters.  # noqa: E501
        :type: GYAssetClass
        """
        if self._configuration.client_side_validation and price_token is None:
            raise ValueError("Invalid value for `price_token`, must not be `None`")  # noqa: E501

        self._price_token = price_token

    @property
    def start(self):
        """Gets the start of this PlaceOrderParameters.  # noqa: E501

        This is the posix time in ISO8601 format.  # noqa: E501

        :return: The start of this PlaceOrderParameters.  # noqa: E501
        :rtype: str
        """
        return self._start

    @start.setter
    def start(self, start):
        """Sets the start of this PlaceOrderParameters.

        This is the posix time in ISO8601 format.  # noqa: E501

        :param start: The start of this PlaceOrderParameters.  # noqa: E501
        :type: str
        """

        self._start = start

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
        if issubclass(PlaceOrderParameters, dict):
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
        if not isinstance(other, PlaceOrderParameters):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PlaceOrderParameters):
            return True

        return self.to_dict() != other.to_dict()
