import logging
import voluptuous as vol
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_FRIENDLY_NAME
import homeassistant.helpers.config_validation as cv
import datetime as dt
from ast import literal_eval

_LOGGER = logging.getLogger(__name__)

# consts
NAME = CONF_FRIENDLY_NAME
DATES = 'dates'
FORMAT = 'format'
FORMAT_NORMAL = 'normal'
FORMAT_DAYS = 'days'
ICON = 'icon'

DATE_FORMAT = "%d.%m.%Y"

# user config validation
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(NAME): cv.string,  # biogarbage
    vol.Required(DATES): cv.string,  # ["01.01.2020","24.12.2020"]
    vol.Optional(ICON, default='mdi:bell-ring'): cv.icon,
    vol.Optional(FORMAT, default=FORMAT_NORMAL): vol.In([FORMAT_NORMAL, FORMAT_DAYS])
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    name = config.get(NAME)
    dates = config.get(DATES)
    format = config.get(FORMAT)
    icon = config.get(ICON)

    # try to parse dates
    try:
        dates = literal_eval(dates)
        dates = [dt.datetime.strptime(date, DATE_FORMAT).date() for date in dates]
    except (ValueError, SyntaxError):
        _LOGGER.error(name + ": dates must be an array like ['01.01.2020', '24.12.2020']")
        return

    add_devices([ReminderSensor(name, dates, format, icon)])


class ReminderSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, dates, format, icon):
        """Initialize the sensor."""
        self._name = name
        self._dates = dates
        self._format = format
        self._icon = icon
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._state in ['today', 'tomorrow']:
            return self._icon
        return "mdi:checkbox-blank-circle-outline"

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        today = dt.date.today()
        try:
            next_date = min(date for date in self._dates if date >= today)
        except ValueError:
            self._state = ''
            _LOGGER.warning(self._name + ': no upcoming date in dates')
        else:
            delta = (next_date - today).days
            if delta == 0:
                self._state = 'today'
            elif delta == 1:
                self._state = 'tomorrow'
            else:
                self._state = next_date.strftime(DATE_FORMAT) if self._format == FORMAT_NORMAL else 'in {} days'.format(delta)