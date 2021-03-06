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

Upstairs normal trigger
+++++++++++++++++++++++

Another scenario is when the system initiates the light from upstairs,  then we
go on the normal timeout for the upstairs,  but we don't light up the downstairs
unitil the sensor comes for it.

Upstairs retrigger
++++++++++++++++++

A third scenario that turns up is that sometimes I am sitting in the pew and the
light goes out and I want to have it go back on.  I propose having a long timeout
(say 15 min) if the lights are turned off and then the motion sensor comes back on.

Data structures needed to support
---------------------------------

So the tricky thing is determining the data structures needed to maintain the
above behavior.

What states can the system be in?

A) No activity
B) Activity at bottom only
C) Activity at top only
D) Bottom moving towards top
E) Top moving towards bottom

It is confusing because it is not a matter of independent zones but rather an
interlocking set of zones.  If we put together the following sets:

(1) Top
(2) South
(3) Bottom

Then some set of those can be selected that are not overlapping but cover the
active lights,  so the meaningful states are (1),  (2),  (3) and (1) + (3).

(2) turns out to be the one that is special in that (2) excludes the others.  (2)
is a metastable state,  it holds for a short time and transitions to either (1) or (3) or
possibly (1) + (3).  Once either (1) or (3) is on,  then the two systems behave
independently.

Is it fair to call those states "scenes"?


