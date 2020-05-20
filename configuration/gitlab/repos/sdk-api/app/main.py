import json
import traceback
import logging
from functools import partial

from flask import Flask, request, render_template, Response
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from marshmallow import ValidationError

from utils import TripRequestShema, auth

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:[%(levelname)s]: %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates'
            )


@app.route('/index')
def main():
    return render_template('index.html')


@app.route('/v1/trip', methods=["POST"])
@auth
def trip():
    serializer = TripRequestShema(unknown="RAISE")
    request_data = request.json
    log.info(f"Request json: {request_data.get('data')}")
    try:
        serializer.load(request.json)
        response = analyze_data(request.json)
        log.info(f"Response data: {response}")
    except ValidationError as err:
        log.error(f"Request validation error: {err}")
        return Response(f"Json validation error: {json.dumps(err.messages)}", 405)
    except GeocoderServiceError as err:
        log.error(traceback.format_exc())
        return Response(f"Can not get geo data, external service error: {traceback.format_exc()}", 500)
    except Exception as e:
        log.error(f"Error while processing request: {traceback.format_exc()}")
        return Response(f"Error: {traceback.format_exc()}", 500)
    return Response(json.dumps(response), 200)


def analyze_data(request_data: dict):
    gasTankSize = request_data["gasTankSize"]
    data = sorted(request_data["data"], key=lambda x: x["timestamp"])  # sort by timetamp
    geopoints = parse_geodata(data)
    breakes = list()
    refuelStops = list()
    vd = request_data["data"]
    fuelCons = 0

    for i, record in enumerate(vd):
        if i != 0:
            if record["fuelLevel"] > vd[i - 1]["fuelLevel"]:
                refuelStops.append({"startTimestamp": vd[i - 1]["timestamp"],
                                    "endTimestamp": record["timestamp"],
                                    "positionLat": record["positionLat"],
                                    "positionLong": record["positionLong"]
                                    })
            if record["timestamp"] - vd[i - 1]["timestamp"] > int(request_data["breakThreshold"]):
                if record["odometer"] == vd[i - 1]["odometer"]:
                    breakes.append({"startTimestamp": vd[i - 1]["timestamp"],
                                    "endTimestamp": record["timestamp"],
                                    "positionLat": record["positionLat"],
                                    "positionLong": record["positionLong"]
                                    })
            if record["fuelLevel"] < vd[i - 1]["fuelLevel"]:
                fuelCons += vd[i - 1]["fuelLevel"] - record["fuelLevel"]

    response = {
        "vin": request_data["vin"],
        "departue": geopoints[0].raw["address"]["city"],
        "destination": geopoints[-1].raw["address"]["city"],
        "refuelStops": refuelStops,
        "breaks": breakes,
        "consumption": (fuelCons * gasTankSize) / (
                request_data["data"][-1]["odometer"] - request_data["data"][0]["odometer"])
    }

    return response


def parse_geodata(points: list):
    locator = Nominatim(user_agent="myapp")  # lib using OpenStreetMap by default
    parsed_locations = list()
    for point in points:
        coord_string = ", ".join([str(point["positionLat"]), str(point["positionLong"])])
        try:
            location = with_retry(3, partial(locator.reverse, coord_string))
        except GeocoderServiceError as err:
            log.error("locator error, probably geo service is unavailable")
            raise err
        address = location.raw["address"]
        log.debug(f"Point address: {address}")

        if "city" not in address.keys():
            address["city"] = address["town"] if "town" in address.keys() else address["state"]

        parsed_locations.append(location)
    return parsed_locations


def with_retry(tries: int, f: partial):
    for i in range(tries):
        try:
            return f()
        except Exception as e:
            log.error(f"{f.func} execution error: {traceback.format_exc()}\nretry {i < tries - 1} more times")
            if i < tries - 1:  # i is zero indexed
                continue
            else:
                raise e


if __name__ == '__main__':
    app.secret_key = 'pupanlupa'
    app.run(host='0.0.0.0', debug=True)
