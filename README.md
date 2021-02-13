# Prototype Virtual Precipitation sensor for Mudpi

## Description
Prototype Sensor for Mudpi which uses the Open Weather API to get weather based precipitation forecast data as events.  This was built on Mudpi-core v0.9.1. I intend on creating a PR to the Mudpi-core project after the next release which has some refactoring.  

The sensor was added to mudpi using the [Extending Mudpi](https://mudpi.app/docs/extending-mudpi) instructions.  Thanks Eric for making Mudpi so easy to expand. 

I am looking for feedback on other forecast weather data which would be valuable in trigger related scenarios.  

This requires creating a account with OpenWeather and generating an API key.  The instructions can be found [here](https://openweathermap.org/appid).  This is a free service if you make less then 1000 api calls per day / 30000 calls per month.  I recommend creating a second worker sensor group (see example) and calling this API only once every 5 or more minutes.  Scenario explained in the [Mudpi Documentation](https://mudpi.app/docs/configuration-workers) 

<br>

## Features

- Looks for max chance of precipitation in x defined hours.  The max percent chance of precipitation is sent as a to the sensor event to be used by triggers.  

- Defaults to your ISP location if you don't know or want to use your specific lat/long location 

- API calls error/networks issues are handled when the service is not reachable.  The sensor failure will not crash the core mudpi app.  Its possible the PI controller has unreliable wifi network connection.  

<br>

## Use cases 

- Don't trigger water pump relay when the soil sensors indicate the garden needs water because in the next 12 hours there is a 90% chance of rain.   

<br>

## Install
1. Install on top of [Mudpi-Core v0.9.1](https://github.com/mudpi/mudpi-core)
2. The installation requires only 2 changes.  
    1. Updating the (mudpi/core/workers/pi/sensor_worker.py) sensor worker 
    2. Defining a new (mudpi/core/sensors/pi/precipitation_sensor.py) sensor
3. Download the new sensor file and update to the pi worker script  
    ```shell
    cd ~/Downloads 
    ```
    ```shell
    wget https://raw.githubusercontent.com/icyspace/Mudpi-VirtualSensor/main/precipitation_sensor.py
    ```
    ```shell
    wget https://raw.githubusercontent.com/icyspace/Mudpi-VirtualSensor/main/sensor_worker.py
    ```
 4. Backup Current sensor worker (assumes default Mudpi Install location)
    ```shell
    sudo mv /etc/mudpi/core/workers/pi/sensor_worker.py /etc/mudpi/core/workers/pi/sensor_worker.bk
    ```

5. Copy new sensor files to mudpi (assumes default Mudpi Install location)
    ```shell
    sudo cp ~/Downloads/precipitation_sensor.py /etc/mudpi/core/sensors/pi/
    ```
    ```shell
    sudo cp ~/Downloads/sensor_worker.py /etc/mudpi/core/workers/pi
    ```
6. Update mudpi.config 
7. Restart mudpi  (see example)
    ```
    sudo supervisorctl restart mudpi 
    ```
8. In Mudpi.log you (in debug mode) you will see 
    ```
    [09:37:51][MudPi][INFO] Sensors...                               Initializing
    [09:37:51][MudPi][DEBUG] PrecipitationSensor: apikey: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    [09:37:51][MudPi][DEBUG] PrecipitationSensor: lat/lon: 44.0000:-92.0000
    [09:37:51][MudPi][DEBUG] PrecipitationSensor: Forecasted Hours to look for precipitation : 12
    [09:37:51][MudPi][DEBUG] PrecipitationSensor: apicall: https://api.openweathermap.org/data/2.5/onecall?lat=44.0000&lon=-92.000&appid=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&units=imperial

    ```    

<br>

## Precipitation Setting


| Option            | Type        |  Required   | Description |
| -----------       | ----------- | ----------- | ----------- |
| **type**              | [String]      |Yes        |  Type of sensor:  Precipitation |
| **pin**               | [Integer]	    |Yes        |  GPIO pin number on raspberry pi the sensor is connected to. In this case use 0 as we are not using any pin this but for sensor this is a required field.           |
| **key**               | [String]	    |Yes        |Key to store value under in redis. Alphanumeric with underscores only. Must be valid redis key.  |
| **openweather_api_key**| String]      |Yes        |[Get OpenWeather API](https://openweathermap.org/appid)|
| **latlong**           | String]       |No         | Defaults to ISP location when not provided.  Provide latitude and longitude in this formate with no spaces:  "lat,long"|
| **forecasted_hours**  | [Integer]	    |No         |  integer between 1 and 24 (defaults to 24 hours) This represents how many hours in the future to look for precipitations |

<br>

---

<br><br>

## Example mudpi.config  
```   "workers": [
        {
            "type": "sensor",
            "sleep_duration":30,
            "sensors": [
                {
                    "type": "Humidity",
                    "pin": 24,
                    "model": "11",
                    "key": "weather_sensor"
                }
            ]
        },
        {
            "type": "sensor",
            "sleep_duration":300,
            "sensors": [
                {
                    "type": "Precipitation",
                    "pin": 0,
                    "key": "precipitation_forecast",
                    "openweather_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "latlong": "44.000000,-93.000000",
                    "forecasted_hours" : 12
                }
            ]
        }
    ],


```
