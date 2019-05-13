"""
Setup for dynamic web server for tentacruel.  Serves content at

   http://localhost:{web_port}/{web_prefix}/

and the assumption is that the front-end web server is configured so that::

   http://{web_server}:80/{web_prefix}/

is proxied to the above.  This makes the dynamic server testable both
locally and remotely.
"""
