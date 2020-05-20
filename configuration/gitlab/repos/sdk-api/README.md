# Vehicle Trip Analyzer

## Endpoints
GET /v1/index.html
Requests generator to test /v1/trip endpoint

POST /v1/trip 
vehicle data analyzer, request type is JSON, it uses HTTP Basic Auth for user authentication, format example:
## POST example
```json
{
    "vin" : "WDD1671591Z000999",
    "breakThreshold" : 1800,
    "gasTankSize" : 100,
    "data" :[
                {
                    "timestamp" : 1589728287,
                    "odometer" : 548,
                    "fuelLevel" : 80,
                    "positionLat" : 55.797226,
                    "positionLong" : 37.538148
                },
                {
                    "timestamp" : 1589738288,
                    "odometer" : 611,
                    "fuelLevel" : 20,
                    "positionLat" : 56.867187,
                    "positionLong" : 35.908777
                },
                {
                    "timestamp" : 1589748289,
                    "odometer" : 698,
                    "fuelLevel" : 100,
                    "positionLat" : 57.580585,
                    "positionLong" : 34.574110
                },
                {
                    "timestamp" : 1589758299,
                    "odometer" : 698,
                    "fuelLevel" : 60,
                    "positionLat" : 58.524382,
                    "positionLong" : 31.286626
                },
                {
                    "timestamp" : 1589798310,
                    "odometer" : 611,
                    "fuelLevel" : 90,
                    "positionLat" : 59.877219,
                    "positionLong" : 30.373989
                }
    ]}
```

returns analyzed vehicle data, in JSON, format example for response code 200:
```json
{   "vin": "WDD1671591Z000999", 
    "departue": "Москва", 
    "destination": "округ Волковское", 
    "refuelStops": [{
        "startTimestamp": 1589728288, 
        "endTimestamp": 1589728289, 
        "positionLat": 57.580585, 
        "positionLong": 34.57411}, 
        {"startTimestamp": 1589728299, 
        "endTimestamp": 1589728310, 
        "positionLat": 59.877219, 
        "positionLong": 30.373989}], 
    "breaks": [], 
    "consumption": 158.73015873015873}
```
In case of error it will return json validation error with the error fields data(code 500), examples:
Request: 
```json
{
    "vin": "WDD1671591Z000999",
    "breakThreshold": 1800,
    "gasTankSize": 100,
    "data": []
}
```

Response:
```json
Json validation error: {"data": ["Shorter than minimum length 1."]}
```

Request:
```json
{
    "vi": "WDD1671591Z000999",
    "breakThreshold": 1800,
    "gasTankSizee": 100,
    "data": [
        {
            "timestamp": 1589728287,
            "odometer": 548,
            "fuelLevel": 80,
            "positionLat": 55.797226,
            "positionLong": 37.538148
        },
        {
            "timestamp": 1589728288,
            "odometer": 611,
            "fuelLevel": 20,
            "positionLat": 56.867187,
            "positionLong": 35.908777
        },
        {
            "timestamp": 1589728289,
            "odometer": 698,
            "fuelLevel": 100,
            "positionLatt": 57.580585,
            "positionLong": 34.57411
        },
        {
            "timestamp": 1589728299,
            "odometer": 698,
            "fuelLevel": 60,
            "positionLat": 58.524382,
            "positionLong": 31.286626
        },
        {
            "timestamp": 1589728310,
            "odometer": 611,
            "fuelLevel": 90,
            "positionLat": 59.877219,
            "positionLong": 30.373989
        }
    ]
}
```
Response:
```json
Json validation error: {"vin": ["Missing data for required field."], "data": {"2": {"positionLat": ["Missing data for required field."], "positionLatt": ["Unknown field."]}}, "gasTankSize": ["Missing data for required field."]}
```
