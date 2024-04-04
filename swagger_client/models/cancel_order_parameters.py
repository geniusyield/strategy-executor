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


class CancelOrderParameters(object):
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
        'order_references': 'list[GYTxOutRef]'
    }

    attribute_map = {
        'address': 'address',
        'collateral': 'collateral',
        'order_references': 'order_references'
    }

    def __init__(self, address=None, collateral=None, order_references=None, _configuration=None):  # noqa: E501
        """CancelOrderParameters - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._address = None
        self._collateral = None
        self._order_references = None
        self.discriminator = None

        self.address = address
        if collateral is not None:
            self.collateral = collateral
        self.order_references = order_references

    @property
    def address(self):
        """Gets the address of this CancelOrderParameters.  # noqa: E501


        :return: The address of this CancelOrderParameters.  # noqa: E501
        :rtype: GYAddressBech32
        """
        return self._address

    @address.setter
    def address(self, address):
        """Sets the address of this CancelOrderParameters.


        :param address: The address of this CancelOrderParameters.  # noqa: E501
        :type: GYAddressBech32
        """
        if self._configuration.client_side_validation and address is None:
            raise ValueError("Invalid value for `address`, must not be `None`")  # noqa: E501

        self._address = address

    @property
    def collateral(self):
        """Gets the collateral of this CancelOrderParameters.  # noqa: E501


        :return: The collateral of this CancelOrderParameters.  # noqa: E501
        :rtype: GYTxOutRef
        """
        return self._collateral

    @collateral.setter
    def collateral(self, collateral):
        """Sets the collateral of this CancelOrderParameters.


        :param collateral: The collateral of this CancelOrderParameters.  # noqa: E501
        :type: GYTxOutRef
        """

        self._collateral = collateral

    @property
    def order_references(self):
        """Gets the order_references of this CancelOrderParameters.  # noqa: E501


        :return: The order_references of this CancelOrderParameters.  # noqa: E501
        :rtype: list[GYTxOutRef]
        """
        return self._order_references

    @order_references.setter
    def order_references(self, order_references):
        """Sets the order_references of this CancelOrderParameters.


        :param order_references: The order_references of this CancelOrderParameters.  # noqa: E501
        :type: list[GYTxOutRef]
        """
        if self._configuration.client_side_validation and order_references is None:
            raise ValueError("Invalid value for `order_references`, must not be `None`")  # noqa: E501

        self._order_references = order_references

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
        if issubclass(CancelOrderParameters, dict):
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
        if not isinstance(other, CancelOrderParameters):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CancelOrderParameters):
            return True

        return self.to_dict() != other.to_dict()
