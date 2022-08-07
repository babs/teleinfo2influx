teleinfo2influx
=======

This piece of software reads data from a serial input of any device able to handle modulated signals from the [teleinformation port of a Linky meter](https://www.enedis.fr/sites/default/files/Enedis-NOI-CPT_54E.pdf) in standard mode.
You can find several dongle, shield or DIY electronic assemblies online.

For the influx part, it relies on telegraf's ability to relay influxdb and buffer datapoints in case of network issue.

Configuration
----

Available environment variables:

* `SERIAL_PORT`: serial port to read from (default `/dev/ttyAMA0`)
* `INFLUXDB_URL`: Influx url to write to (default `http://127.0.0.1:8186/write`)

Installation 
===

* clone into `/opt/teleinfo2influx`
* symlink or copy `teleinfo2influx.service` into `/etc/systemd/system/`
* reload systemd `systemctl daemon-reload`
* enable and start the service `systemctl enable --now teleinfo2influx`
* configure your telegraf instance using the following snippet
* restart your telegraf instance

telegraf configuration
-------

    [[inputs.influxdb_listener]]
    service_address = "127.0.0.1:8186"
    parser_type = "upstream"

