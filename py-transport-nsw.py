"""
Transport NSW (AU) sensor to query next leave event for a specified stop.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.transport_nsw/
"""
from datetime import timedelta
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_API_KEY, ATTR_ATTRIBUTION)

REQUIREMENTS = ['PyTransportNSW==0.1.1']

_LOGGER = logging.getLogger(__name__)

ATTR_STOP_ID = 'stop_id'
ATTR_ROUTE = 'route'
ATTR_DUE_IN = 'due'
ATTR_DELAY = 'delay'
ATTR_REAL_TIME = 'real_time'
ATTR_DESTINATION = 'destination'
ATTR_MODE = 'mode'
ATTR_STOP_LAT = 'stop_latitude' 
ATTR_STOP_LNG = 'stop_longitude'
ATTR_BUS_LAT = 'bus_latitude'
ATTR_BUS_LNG = 'bus_longitude'

CONF_ATTRIBUTION = "Data provided by Transport NSW"
CONF_STOP_ID = 'stop_id'
CONF_ROUTE = 'route'
CONF_DESTINATION = 'destination'

DEFAULT_NAME = "Next Bus"
ICONS = {
    'Train': 'mdi:train',
    'Lightrail': 'mdi:tram',
    'Bus': 'mdi:bus',
    'Coach': 'mdi:bus',
    'Ferry': 'mdi:ferry',
    'Schoolbus': 'mdi:bus',
    'n/a': 'mdi:clock',
    None: 'mdi:clock'
}

SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOP_ID): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ROUTE, default=""): cv.string,
    vol.Optional(CONF_DESTINATION, default=""): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Transport NSW sensor."""
    stop_id = config[CONF_STOP_ID]
    api_key = config[CONF_API_KEY]
    route = config.get(CONF_ROUTE)
    destination = config.get(CONF_DESTINATION)
    name = config.get(CONF_NAME)

    data = PublicTransportData(stop_id, route, destination, api_key)
    add_entities([TransportNSWSensor(data, stop_id, name)], True)


class TransportNSWSensor(Entity):
    """Implementation of an Transport NSW sensor."""

    def __init__(self, data, stop_id, name):
        """Initialize the sensor."""
        self.data = data
        self._name = name
        self._stop_id = stop_id
        self._times = self._state = None
        self._icon = ICONS[None]
        self.gps = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._times is not None:
            return {
                ATTR_DUE_IN: self._times[ATTR_DUE_IN],
                ATTR_STOP_ID: self._stop_id,
                ATTR_ROUTE: self._times[ATTR_ROUTE],
                ATTR_DELAY: self._times[ATTR_DELAY],
                ATTR_REAL_TIME: self._times[ATTR_REAL_TIME],
                ATTR_DESTINATION: self._times[ATTR_DESTINATION],
                ATTR_MODE: self._times[ATTR_MODE],
                ATTR_STOP_LAT: self._times[ATTR_STOP_LAT],
                ATTR_STOP_LNG: self._times[ATTR_STOP_LNG],
                ATTR_BUS_LAT: self._times[ATTR_BUS_LAT],
                ATTR_BUS_LNG: self._times[ATTR_BUS_LNG],
                ATTR_ATTRIBUTION: CONF_ATTRIBUTION
            }

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return 'min'

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Get the latest data from Transport NSW and update the states."""
        self.data.update()
        self._times = self.data.info
        self._state = self._times[ATTR_DUE_IN]
        self._icon = ICONS[self._times[ATTR_MODE]]

class PublicTransportData:
    """The Class for handling the data retrieval."""

    def __init__(self, stop_id, route, destination, api_key):
        """Initialize the data object."""
        import TransportNSW

        self._stop_id = stop_id
        self._route = route
        self._destination = destination
        self._api_key = api_key
        self.info = { ATTR_ROUTE: self._route,
                     ATTR_DUE_IN: 'n/a',
                     ATTR_DELAY: 'n/a',
                     ATTR_REAL_TIME: 'n/a',
                     ATTR_DESTINATION: 'n/a',
                     ATTR_MODE: None,
                     ATTR_STOP_LAT: 'n/a', 
                     ATTR_STOP_LNG: 'n/a',
                     ATTR_BUS_LAT: 'n/a',
                     ATTR_BUS_LNG: 'n/a'}
        self.tnsw = TransportNSW.TransportNSW()

    def update(self):
        """Get the next leave time."""
        _data = self.tnsw.get_departures(self._stop_id,
                                         self._route,
                                         self._destination,
                                         self._api_key)
        # print("received departures")
        # print(_data)

        _bus_location = self.tnsw.get_bus_gps(_data,
                                         self._api_key)

        # print("received bus location")
        # print(_bus_location)

        self.info = {ATTR_ROUTE: _data['route'],
                     ATTR_DUE_IN: _data['due'],
                     ATTR_DELAY: _data['delay'],
                     ATTR_REAL_TIME: _data['real_time'],
                     ATTR_DESTINATION: _data['destination'],
                     ATTR_MODE: _data['mode'],
                     ATTR_STOP_LAT: _data[ATTR_STOP_LAT],
                     ATTR_STOP_LNG: _data[ATTR_STOP_LNG],
                     ATTR_BUS_LAT: _bus_location[ATTR_BUS_LAT],
                     ATTR_BUS_LNG: _bus_location[ATTR_BUS_LNG]}
