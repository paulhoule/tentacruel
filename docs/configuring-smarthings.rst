Configuring SmartThings
=======================

Today I am setting up the Sengled switch to control the Phillips Hue light.  The Sengled
switch has been attached to SmartThings for a long time,  the battery is strong because I
haven't been pushing on it.

The events were getting to SmartThings but not progressing through the lambda function
and to the drain-q process on Tamamo,  where the light control "business logic" lives.

To resolve I had to remove and reinstall
the "472Central" application from the SmartThings console by hand,  in the Android
Emulator.  I did that and I was fine.

I had to experiment to create a lambda function by hand that would really get
events from SmartThings -- I would attempt to register,  not seem to get an error
message,  but not events.  Two strategies that helped were:

(1) Register different capability listeners separately:  sometimes asking for
two many different kinds of permission may jam things up.

(2) Register different devices separately:  seems to be a problem that S.T. won't
let you listen for events on all switches,  probably because you could blow up your smart
house responding to switches switching other switches endlessly.

Plan:  use multiple instances of the same lambda function to register various
event types we want to listen to.
