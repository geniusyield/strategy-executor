# coding: utf-8

"""
    GeniusYield DEX Server API

    API to interact with GeniusYield DEX.  # noqa: E501

    OpenAPI spec version: 0.0.1
    Contact: support@geniusyield.co
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from swagger_client.configuration import Configuration


class OrderInfo(object):
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
        'end': 'str',
        'offer_amount': 'str',
        'output_reference': 'GYTxOutRef',
        'owner_address': 'GYAddressBech32',
        'owner_key_hash': 'GYPubKeyHash',
        'price': 'str',
        'start': 'str'
    }

    attribute_map = {
        'end': 'end',
        'offer_amount': 'offer_amount',
        'output_reference': 'output_reference',
        'owner_address': 'owner_address',
        'owner_key_hash': 'owner_key_hash',
        'price': 'price',
        'start': 'start'
    }

    def __init__(self, end=None, offer_amount=None, output_reference=None, owner_address=None, owner_key_hash=None, price=None, start=None, _configuration=None):  # noqa: E501
        """OrderInfo - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._end = None
        self._offer_amount = None
        self._output_reference = None
        self._owner_address = None
        self._owner_key_hash = None
        self._price = None
        self._start = None
        self.discriminator = None

        if end is not None:
            self.end = end
        self.offer_amount = offer_amount
        self.output_reference = output_reference
        self.owner_address = owner_address
        self.owner_key_hash = owner_key_hash
        self.price = price
        if start is not None:
            self.start = start

    @property
    def end(self):
        """Gets the end of this OrderInfo.  # noqa: E501

        This is the posix time in ISO8601 format.  # noqa: E501

        :return: The end of this OrderInfo.  # noqa: E501
        :rtype: str
        """
        return self._end

    @end.setter
    def end(self, end):
        """Sets the end of this OrderInfo.

        This is the posix time in ISO8601 format.  # noqa: E501

        :param end: The end of this OrderInfo.  # noqa: E501
        :type: str
        """

        self._end = end

    @property
    def offer_amount(self):
        """Gets the offer_amount of this OrderInfo.  # noqa: E501


        :return: The offer_amount of this OrderInfo.  # noqa: E501
        :rtype: str
        """
        return self._offer_amount

    @offer_amount.setter
    def offer_amount(self, offer_amount):
        """Sets the offer_amount of this OrderInfo.


        :param offer_amount: The offer_amount of this OrderInfo.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and offer_amount is None:
            raise ValueError("Invalid value for `offer_amount`, must not be `None`")  # noqa: E501

        self._offer_amount = offer_amount

    @property
    def output_reference(self):
        """Gets the output_reference of this OrderInfo.  # noqa: E501


        :return: The output_reference of this OrderInfo.  # noqa: E501
        :rtype: GYTxOutRef
        """
        return self._output_reference

    @output_reference.setter
    def output_reference(self, output_reference):
        """Sets the output_reference of this OrderInfo.


        :param output_reference: The output_reference of this OrderInfo.  # noqa: E501
        :type: GYTxOutRef
        """
        if self._configuration.client_side_validation and output_reference is None:
            raise ValueError("Invalid value for `output_reference`, must not be `None`")  # noqa: E501

        self._output_reference = output_reference

    @property
    def owner_address(self):
        """Gets the owner_address of this OrderInfo.  # noqa: E501


        :return: The owner_address of this OrderInfo.  # noqa: E501
        :rtype: GYAddressBech32
        """
        return self._owner_address

    @owner_address.setter
    def owner_address(self, owner_address):
        """Sets the owner_address of this OrderInfo.


        :param owner_address: The owner_address of this OrderInfo.  # noqa: E501
        :type: GYAddressBech32
        """
        if self._configuration.client_side_validation and owner_address is None:
            raise ValueError("Invalid value for `owner_address`, must not be `None`")  # noqa: E501

        self._owner_address = owner_address

    @property
    def owner_key_hash(self):
        """Gets the owner_key_hash of this OrderInfo.  # noqa: E501


        :return: The owner_key_hash of this OrderInfo.  # noqa: E501
        :rtype: GYPubKeyHash
        """
        return self._owner_key_hash

    @owner_key_hash.setter
    def owner_key_hash(self, owner_key_hash):
        """Sets the owner_key_hash of this OrderInfo.


        :param owner_key_hash: The owner_key_hash of this OrderInfo.  # noqa: E501
        :type: GYPubKeyHash
        """
        if self._configuration.client_side_validation and owner_key_hash is None:
            raise ValueError("Invalid value for `owner_key_hash`, must not be `None`")  # noqa: E501

        self._owner_key_hash = owner_key_hash

    @property
    def price(self):
        """Gets the price of this OrderInfo.  # noqa: E501


        :return: The price of this OrderInfo.  # noqa: E501
        :rtype: str
        """
        return self._price

    @price.setter
    def price(self, price):
        """Sets the price of this OrderInfo.


        :param price: The price of this OrderInfo.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and price is None:
            raise ValueError("Invalid value for `price`, must not be `None`")  # noqa: E501

        self._price = price

    @property
    def start(self):
        """Gets the start of this OrderInfo.  # noqa: E501

        This is the posix time in ISO8601 format.  # noqa: E501

        :return: The start of this OrderInfo.  # noqa: E501
        :rtype: str
        """
        return self._start

    @start.setter
    def start(self, start):
        """Sets the start of this OrderInfo.

        This is the posix time in ISO8601 format.  # noqa: E501

        :param start: The start of this OrderInfo.  # noqa: E501
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
        if issubclass(OrderInfo, dict):
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
        if not isinstance(other, OrderInfo):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OrderInfo):
            return True

        return self.to_dict() != other.to_dict()
