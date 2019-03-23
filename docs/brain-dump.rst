Building an Home IoT System
---------------------------

Intro
=====

(For purposes of my video I am likely to leave out the HEOS system stuff because it is getting to be too much.)

Today I'm going to talk about the internet of things system that I built at home.

You can get products from quite a few different vendors,  and you can often get prebuilt integrations,
but I wanted to pick and choose best of breed hardware for each purpose and also have complete control
of how it makes decisions on my own computer.  The goal here is not just to use "smart home" peripherals
but also have access to online services (such as weather reports) as well as network use,  email,
calendars,  e-commerce and everything that is easy for computers to work with.

Dramatus Personae
=================

1. ZooZ 4-in-1 sensor

2. Samsung SmartThings

3. AWS Lambda

4. Amazon SQS

5. Connector script that transfers events to RabbitMQ

6. RabbitMQ

7. Python script that controls...

8. Phillips Hue

9. HEOS Speaker system

10. Smart Plugs

11. AWS Polly

12. Wi-Fi based presence detection (ping) to know if TV is turned on,  phones have been brought home,  etc.

Goals for the system
====================

1. Wake up sequence:  turn on lights in bedroom and upstairs around sunrise.  Play two songs 15 minutes apart to
   simulate a military style wake-up.  A smart plug can be used to turn on an electric heater in the bathroom
   to prepare for a shower.

2. Full automation of lights:  for the wake up sequence to work,  all of the lights it controls have to be
   turned on.  We still have ordinary switches on our lights,  so that won't be the case unless people
   can leave the lights turned on when they want.

3. "Defend" self-maintainance program that finds lights that have been turned off and asks politely to
   have them switched back on.

 ZooZ 4-in-1 sensor
 ==================

 http://getzooz.com/zooz-zse40-4-in-1-sensor.html

 This is a nice piece of hardware.  I live in a house that has no central heat,  but I have a propane
 heater and a wood stove.  The internal climate varies a lot and this sensor lets me keep on top of it
 with

 * temperature
 * humidity
 * motion sensing
 * illuminance

 as well as

 * vibration
 * tamper sensoring

 as a bonus.  This sensor can run for months powered by a CR123A battery.

 The sensor comes with a screw mounting kit and a strip of double sided sticky foam that lets you
 stick it up within seconds.  The adhesive strips with it do pretty well but the sensor sometimes
 fall off and they won't stick back on reliably if you peel them off.  Similar foam strips can be
 found at the hardware store and I get great results when I use two of those scripts side-by-side.

 The ZooZ sensor connects with Z-Wave to...

 The Samsung SmartThings Hub
 ===========================

 I have the V2 version of the SmartThings Hub.  It can connect via WiFi but I have it connected
 through Ethernet,  as I have the Hue Hub,  because I am concerned that the WiFi radio will
 interfere with Zigbee and Z-Wave.

 I have the V2 version of the SmartThings Hub.  It can connect via WiFi but I have it connected
 through Ethernet,  as I have the Hue Hub,  because I am concerned that the WiFi radio will
 interfere with Zigbee,  which also uses the 2.4 GHz.

 (Z-Wave works in the the 900-MHz band and doesn't compete with WiFi, Bluetooth, Zigbee,  etc.)

 Initial setup of the SmartThings Hub requires a mobile app,  as does pairing,  but you can do
 quite a bit through the web interface.  Particularly,  you can install drivers to add support for
 devices such as the Z-Wave Hub.

https://github.com/krlaframboise/SmartThings/tree/master/devicetypes/krlaframboise/zooz-4-in-1-sensor.src

The device handler is a groovy script that you can cut-and-paste into the web interface.

The Smartthings Hub is popular and widely compatible,  however it runs most device handlers in the
AWS cloud.  Rather than integrating directly to the Hub on the LAN,  we have to connect to the
Smartthing API through the greater internet.  Some people don't like this on principle,  but the
worst problem I've experienced with it is that no internet connection is entirely reliable and that
sometimes notifications get delayed if my connection is heavily loaded.

Practically though,  you need to have a server running in order to get callbacks from SmartThings.
It's a pain to run a server on a home internet connection (firewalls,  changing IP addresses,  etc.)
Running a server outside can get expensive because it has to be sized for peak demand although it
sits idle most of the time.

AWS Lambda
==========

Fortunately,  SmartThings has a close integration with the AWS cloud.  SmartThings locates it's
cloud component in the AWS region which is closest to you.  I live in upstate New York,  so in my case,  that is us-east-2,
based in Ohio.  (My ping is maybe 10-15 ms quicker than it is to us-east-1 in Virgina)

A SmartThings SmartApp works by registering a callback function.  This could be a REST Web
Service call,  or it can be sent directly to an AWS Lambda function.  Since we are in the same
region,  this is wicked fast.

I'd like to point out a few interesting things about this API.

https://smartthings.developer.samsung.com/docs/guides/smartapps/basics.html

The SmartApp is a Lambda function that can be called with several different messages.

At the beginning PING,  CONFIGURATION and INSTALL are used to connect with SmartThings,  have the user give permission to
access devices with the SmartThings mobile app,  and then get complete information about the configuration (e.g. a list
of devices)

The INSTALL phase is special because it is the only phase in which you get a long-lasting refresh token to connect with the
SmartThings API.  This token is good for 30 days and can be renewed.  It is necessary if your SmartApp is going to connect
to SmartThings whenever it wants -- and the INSTALL phase is the only time you can get it.

Later on,  when EVENT(s) happen in the system,  such as motion being detected,  the EVENT data packet comes with a
complete description of the devices,  however in this case you get an access token that lasts only five minutes and
cannot be renewed.  It is easy to use this token to make API requests to the SmartThings system (e.g. turn on a fan) in
response to response to EVENT(s)

A Lambda Function SmartApp can use many forms of persistence,  such as Amazon S3 or DynamoDB.  Since you get so much
in the EVENT message,  however,  you may be able to make a lambda function which is entirely stateless,  as is ours.

In fact,  the only thing that my Lambda function does in response to an EVENT is remove the parts of the message that
we don't need (the device configuration) and store only the minimum amount of information required.  If we throw away
unneeded information early on,  we put less of a load on the all of the systems downstream,  such as the SQS queue,
the internet connection back to my house,  the database that events are logged in,  etc.

I put my Lambda function in with the web user interface that let me edit a single Python file in my web browser.
This is about 150 lines of code::

      import json
      import boto3
      import uuid
      import logging
      import botocore.vendored.requests as requests

      logger = logging.getLogger()
      null = None
      true = True

      main_capabilities = [
        "battery",
        "illuminanceMeasurement",
        "temperatureMeasurement",
        "relativeHumidityMeasurement",
        "motionSensor",
        "accelerationSensor",
      ]

      def configuration(configurationData):
          return {
              "configurationData": {
              "initialize": {
                    "name": "472-message-queue",
                    "description": "472 Message Queue",
                    "id": "app",
                    "permissions": [
                      "r:devices:*"
                    ],
                    "firstPageId": "1"
                  }
              },
              "statusCode": 200
          }

      def page(configurationData):
          return {
            "configurationData": {
              "page": {
                "pageId": "1",
                "name": "Give me authority",
                "nextPageId": null,
                "previousPageId": null,
                "complete": true,
                "sections": [
                  {
                    "name": "Notify message queue about...",
                    "settings": [
                      {
                        "id": "sensor",
                        "name": "Which sensor?",
                        "description": "Tap to set",
                        "type": "DEVICE",
                        "required": true,
                        "multiple": true,
                        "capabilities": main_capabilities,
                        "permissions": [
                          "r"
                        ]
                      }
                    ]
                  }
                ]
              }
            }
          }


      def lambda_handler(event, context):
          logger.warning(event)
          lifecycle = event["lifecycle"]
          if lifecycle == "CONFIGURATION":
              phase = event["configurationData"]["phase"]
              if phase == "INITIALIZE":
                  return configuration(event["configurationData"])
              elif phase == "PAGE":
                  return page(event["configurationData"])
              return {
                  "statusCode" : "404",
                  "reason": "your phase doesn't exist and you should feel bad."
              }

          if lifecycle == "INSTALL":
            authToken = event["installData"]["authToken"]
            installedAppId = event["installData"]["installedApp"]["installedAppId"]
            locationId = event["installData"]["installedApp"]["locationId"]
            url = f"https://api.smartthings.com/installedapps/{installedAppId}/subscriptions"
            for capability in main_capabilities:
              command = {
                "sourceType": "CAPABILITY",
                "capability": {
                  "locationId": locationId,
                  "capability": capability,
                  "attribute": "*",
                  "value": "*",
                  "subscriptionName": f"all_{capability}_sub"
                }
              }

              headers = {
                "Authorization": f"Bearer {authToken}"
              }

              response = requests.post(url,json=command,headers=headers)
              if response.status_code == 200:
                logger.warning("Set subscription successfully")
              else:
                logger.error(f"Got {response.status_code} while attempting to subscribe to events")
                return {
                  "statusCode": 500
                }

            return {
              "installData": {}
            }

          if lifecycle == "UNINSTALL":
            return {
              "uninstallData": {}
            }

          if lifecycle == "UPDATE":
            return {
              "updateData": {}
            }

          if lifecycle == "EVENT":
            client = boto3.client('sqs')
            events = event["eventData"]["events"]
            for item in events:
              deviceEvent = item["deviceEvent"]
              del deviceEvent["locationId"]
              del deviceEvent["componentId"]
              del deviceEvent["capability"]
              del deviceEvent["valueType"]
              del deviceEvent["subscriptionName"]

            client.send_message(
                QueueUrl = "https://sqs.us-east-2.amazonaws.com/741501118166/472SmartThings.fifo",
                MessageBody = json.dumps(events),=-
                MessageGroupId = "SmartThingsEvent",
                MessageDeduplicationId = str(uuid.uuid4())
            )

            return {
                'eventData': {}
            }

In addition to the Lambda function code,  I had to grant permissions for the lambda function to post messages
to the SQS queue with Amazon's IAM management console that lets you grant permissions to access Amazon service
which just a few clicks.  This way a program like this doesn't need to store passwords,  API Keys,  or other
credentials to get things done.

Amazon SQS
==========

Message queues such as Amazon SQS are a common component of internet of things systems because they can
paper over many non-idealities in this world.  The server in my house,  for instance,  can receive messages
from the message queue by making an http request to the AWS.  It doesn't have to have a port open to take
requests from outside the home.  If my server fails to request messages for a while,  the messages will get backlogged
but will still be available the next time it requests messages.  A device which only connects to the network
sporadically can send and receive messages to other parts of the system.

Put together with other kinds of message-oriented middleware,  such as Amazon SNS,  message queues work a lot like
"instant messaging for machines".

Rabbit MQ and Gateway Script
============================

A small Python script on the home server (Tamamo) requests messages from the message queue from SQS and copies
them to my server