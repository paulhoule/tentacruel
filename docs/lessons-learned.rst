Lessons Learned
===============

This function seems way too complicated::

    async def add_to_queue(self,sid=None,cid=None,mid=None,aid=None,pid=None):
        if pid==None:
            pid=self._player_id

        if aid==None:
            aid=4

        arguments = dict(
            pid=pid,
            aid=aid
        )
        if sid:
            arguments["sid"] = sid
        if cid:
            arguments["cid"] = cid
        if mid:
            arguments["mid"] = mid

        return await self._run(
            "add_to_queue",
            arguments = arguments
        )
        
A few problems I see with it are:

  * almost all the methods of this type have two lines to compute the default pid
  * we are setting ``aid=None`` as the default and later replacing ``None`` with ``4``;  why not
    just say ``aid=4`` in the parameter list?  (I haven't changed it yet because I think I
    may be relying on passing in ``None`` in the ``aid`` when I call it and have that default
    to 4 also.
   * ``pid`` and ``aid`` are always present so they are declared in the dict constructor
   * but ``sid``,  ``cid``,  and ``mid`` use a different pattern to handle the optional case.
   * the return at the end is not so bad,  but like the pid default,  it is copied in every
     method
   * less visibily,  the kind of code is not clear about typing,  for instance we are setting "aid"
     as an integer 4 here and then later turning it into a string through automatic coercion.  This
     does the right thing almost always,  except when we try to compare ``4`` with ``"4"`` and they
     are not equal!
     
 This kind of stub is common,  so learning to write better stubs is worthwhile.  Here are some
 solutions:
 
   * make up our mind,  this is an object-oriented API,  if you want to use a different pid just get
     a different object.  If we want to add more value we could stash other player-specific variables
     in this object
   * more declarative declaration of inputs and outputs
