How lights are grouped
======================

Lights:
-------

* Upstairs South
* Upstairs North
* Downstairs Hallway
* Downstairs Main

Sensors:
--------

* Upstairs South
* Upstairs North
* Upstairs Mid
* Downstairs Hallway

Some scenarios
--------------

Downstairs Hallway triggered alone
++++++++++++++++++++++++++++++++++

Ok,  when the downstairs hallway is triggered,  we don't know if the intention was
to be in the downstairs area or to go upstairs.

If the user wants to go up stairs then we will see them go up the stairs in 30
seconds or so.

We still want to get the jump on sensing if somebody is going up the stairs,  so I
am going to say that the system should turn on the Downstairs Hallway and Upstairs
South,  but have a shorter timeout on the Upstairs south.  If we see

Downstairs -> Upstairs

we should turn off the downstairs as soon as the motion sensor turns up inactive
downstairs.

Another scenario is when the system initiates the light from upstairs,  then we
go on the normal timeout for the upstairs,  but we don't light up the downstairs
unitl the sensor comes for it.

A third scenario that turns up is that sometimes I am sitting in the pew and the
light goes out and I want to have it go back on.  I propose having a long timeout
(say 15 min) if the lights are turned off and then the motion sensor comes back on.


