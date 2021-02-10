import time
import json
import redis
import requests
import datetime

from .sensor import Sensor
from logger.Logger import Logger, LOG_LEVEL


class PrecipitationSensor(Sensor):

    def __init__(self, pin, openweather_api_key=None, latlong=None, forecasted_hours=24, name=None, key=None,
                 redis_conn=None):
        super().__init__(pin, name=name, key=key, redis_conn=redis_conn)
        self.apikey = openweather_api_key
        self.location = latlong
        self.noHours = forecasted_hours
        return

    def init_sensor(self):
        # Initialize the sensor here (i.e. set pin mode, get addresses, etc) this gets called by the worker
        # Check for API key
        if self.apikey is None:
            Logger.log(LOG_LEVEL["error"], 'PrecipitationSensor: openweather_api_key not set')

        apikey = self.apikey
        Logger.log(LOG_LEVEL["debug"], 'PrecipitationSensor: apikey: ' + str(apikey))

        # lookup location if not provided
        if self.location is None:
            # Get location of device if not provided
            try:
                r = requests.get('https://ipinfo.io/')
                j = json.loads(r.text)
                loc = tuple(j["loc"].split(','))
                Logger.log(LOG_LEVEL["debug"],
                           "PrecipitationSensor: Forecast based on device location: " + j["city"] + ", " + j[
                               "region"] + ", " + j["country"])
            except Exception as e:
                Logger.log(LOG_LEVEL["error"], "PrecipitationSensor: Unable to retrieve location: " + str(e))

        else:

            loc = self.location.split(',')

        lat = loc[0]
        lon = loc[1]
        Logger.log(LOG_LEVEL["debug"], 'PrecipitationSensor: lat/lon: ' + str(lat) + ':' + str(lon))
        Logger.log(LOG_LEVEL["debug"], 'PrecipitationSensor: Forecasted Hours to look for precipitation : ' + str(self.noHours))

        self.sensor = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=imperial" % (
            lat, lon, apikey)
        Logger.log(LOG_LEVEL["debug"], 'PrecipitationSensor: apicall: ' + str(self.sensor))

        return

    def read(self):
        try:
            response = requests.get(self.sensor)
            data = json.loads(response.text)

            hours = int(self.noHours)
            currentts = datetime.datetime.now().timestamp()
            maxpop = 0.0
            # Identify the max pop for the forecasted windows
            for h in data["hourly"]:
                if h["pop"] > maxpop and h["dt"] < currentts + (hours * 3600) and h["dt"] > currentts:
                    maxpop = h["pop"]
                value = float(maxpop)
        except Exception as e:
            Logger.log(LOG_LEVEL["error"], "PrecipitationSensor: Open Weather API call Failed: " + str(e))
            return

        return value
