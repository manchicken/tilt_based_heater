# Tilt-Based Heater Controller

This is a simple heater controller that I wrote based off of the Tilt floating hydrometer,
as well as Digital Loggers AC/DC Control Relay.

In order to build this, you need the `gpiozero` module.

I configure the Tilt to log to the device (the Pi, in this case). Then I use this script which watches that log file, parses out relevant fields, and then controls the AC/DC relay.

Note: I use GPIO port 26 right now. I'll likely make this a config entry at some point, but right now it's in the script.

I added a few safeties:

- If I can't parse the date or the temperature, I turn the heat off.
- If it's been too long (15 minutes) since I've seen an entry in the Tilt log file, I turn the heat off just in case the Tilt service bombed.
- I always default to turning the heat off. I don't know what the heat source is, so it might not be safe to leave the heat on.

## References

- [Digital Loggers AC/DC Control Relay](https://www.pishop.us/product/iot-power-relay-version-2/) ([Docs on relay](http://www.digital-loggers.com/iot2spec.pdf))
- [Tilt Floating Hydrometer](https://tilthydrometer.com/)
- [Set up NodeRed for Tilt](https://tilthydrometer.com/blogs/news/install-tilt-pi-on-raspbian-buster-compatible-with-all-rpi-models-including-rpi-4)
