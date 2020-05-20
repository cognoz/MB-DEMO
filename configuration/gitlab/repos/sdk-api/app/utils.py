import re
import traceback

from decorator import decorator
from flask import request, Response
from marshmallow import Schema, fields
from marshmallow.validate import Range, Regexp, Length

auth_str = "NBXbG5ixoMM22xrMHCzwZs2fJxBKlUgE2mlwfyy4iDXhczKyP6qtgvnfE1UTS2UqkX3gt5DxoCT3KushjJx3wg=="


class ToStrRegexp(Regexp):
    """
    Override Regexp validator for converting input value to string
    """

    def __call__(self, value):
        return super().__call__(str(value))


lat_regexp_validator = ToStrRegexp(
    re.compile("^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$"))
long_regexp_validator = ToStrRegexp(
    re.compile("^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$"))

"""
gps regex matches next formats:
+90.0, -127.554334
45, 180
-90, -180
-90.000, -180.0000
+90, +180
47.1231231, 179.99999999
"""

timestamp_validator = Range(0, 2**31)

class DataPointSchema(Schema):
    timestamp = fields.Int(required=True, validate=[timestamp_validator])
    odometer = fields.Int(required=True)
    fuel_level = fields.Int(required=True, data_key="fuelLevel",
                            validate=[Range(0, 100, error="fuelLevel value must bee between 0 and 100")])  # percent
    pos_lat = fields.Float(required=True, data_key="positionLat", validate=[lat_regexp_validator])
    pos_long = fields.Float(required=True, data_key="positionLong", validate=[long_regexp_validator])


class TripRequestShema(Schema):
    """example:
    {
      "vin": "WDD1671591Z000999",
      "breakThreshold": "1800",
      "gasTankSize": "80",
      "data": [
        {
          "timestamp": "1559137020",
          "odometer": "7200",
          "fuelLevel": 52,
          "positionLat": "48.771990",
          "positionLong": "9.172787"
        }
      ]
    }"""
    vin = fields.Str(required=True)
    break_threshold = fields.Int(required=True, data_key='breakThreshold')
    gas_tank_size = fields.Int(required=True, data_key='gasTankSize')
    data = fields.List(fields.Nested(DataPointSchema), required=True, validate=[Length(min=1)])


@decorator
def auth(f, *args, **kwargs):
    """
    Http handler auth decorator, checks http basic auth
    :param f:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header == f"Basic {auth_str}" or not auth_header:
            return Response(status=401)
        else:
            return f(*args, **kwargs)
    except Exception as e:
        return Response(traceback.format_exc(), 500)
