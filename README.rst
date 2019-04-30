Tentracruel
===========

Home automation framework.  Supports:

* Denon/Marantz HEOS devices
* Denon/Marantz
* Phillips Hue
* Samsung Smartthings Hub
* ZooZ sensors
* National Weather Service Radar and METAR
* Tracking presence/absense of LAN devices and WAN paths using ICMP Ping
* Amazon SQS message queue

Some features include:

* Command line scripting
* GUI to play music
* GUI to observe system state
* Periodic construction of weather reports
* Morning wake-up sequence
* Motion-activated lighting
* Logging of events in arangodb database

This library uses `asyncio` as much as possible.  Many things are lumped together which
would ideally be organized into separate projects,  however:

1. The correct organization was unknown when I started this project,
2. Is still accumulating features as the architecture develops
3. Is more deployable given that all features are deployed in a single virtualenv.

Roughly the Python build and dependency resolution system is flawed and incomplete.  We can't
count on installing an unlimited selection of dependencies in any one virtualenv.  In particular,
if we use the system Python,  the risk is great that we'll install a library that breaks some
other Python-based system or that tentacruel will be broken by a library installed to support
one system.

With one package that runs in one virtualenv there is just one system that needs to be
dealt with if I need to make an emergency change at 4am.

