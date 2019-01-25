# py-transport-nsw
Home assistant sensor for transport nsw that includes next bus GPS location


This is a rebuild of the current home-assistant transport_nsw sensor 
https://home-assistant.io/components/sensor.transport_nsw/


This sensor requires an api key that has access to the following two transportNSW Open Data APIs:
- [Public Transport - Realtime Vehicle Positions](https://opendata.transport.nsw.gov.au/dataset/public-transport-realtime-vehicle-positions) 
- [Trip Planner APIs](https://opendata.transport.nsw.gov.au/dataset/trip-planner-apis)

Get started with the Transport NSW Open Data APIs [here](https://opendata.transport.nsw.gov.au/get-started).





Requirements:

- pip3 install protobuf
- pip3 install gtfs-realtime-bindings





Copy py-transport-nsw to:  %config%\custom_components\sensor