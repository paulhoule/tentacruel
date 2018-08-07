   HEOS CLI Protocol Specification

1. `Overview <#overview>`__

2. `Connection <#connection>`__

   1. `Controller Design Guidelines <#controller-design-guidelines>`__

      1. `Driver Initialization <#driver-initialization>`__

      2. `Caveats <#caveats>`__

      3. `Miscellaneous <#miscellaneous>`__

3. `Command and Response Overview <#command-and-response-overview>`__

   2. `Commands <#commands>`__

   3. `Responses <#responses>`__

4. `Command and Response Details <#command-and-response-details>`__

   4. `System Commands <#system-commands>`__

      4.  `Register for Change Events <#register-for-change-events>`__

      5.  `HEOS Account Check <#heos-account-check>`__

      6.  `HEOS Account Sign In <#heos-account-sign-in>`__

      7.  `HEOS Account Sign Out <#heos-account-sign-out>`__

      8.  `HEOS System Heart Beat <#heos-system-heart-beat>`__

      9.  `HEOS Speaker Reboot <#heos-speaker-reboot>`__

      10. `Prettify JSON response <#prettify-json-response>`__

   5. `Player Commands <#player-commands>`__

      11. `Get Players <#get-players>`__

      12. `Get Player Info <#get-player-info>`__

      13. `Get Play State <#get-play-state>`__

      14. `Set Play State <#_bookmark22>`__

      15. `Get Now Playing Media <#get-now-playing-media>`__

      16. `Get Volume <#get-volume>`__

      17. `Set Volume <#set-volume>`__

      18. `Volume Up <#volume-up>`__

      19. `Volume Down <#volume-down>`__

      20. `Get Mute <#get-mute>`__

      21. `Set Mute <#_bookmark29>`__

      22. `Toggle Mute <#toggle-mute>`__

      23. `Get Play Mode <#get-play-mode>`__

      24. `Set Play Mode <#set-mute>`__

      25. `Get Queue <#get-queue>`__

      26. `Play Queue Item <#play-queue-item>`__

      27. `Remove Item(s) from Queue <#remove-items-from-queue>`__

      28. `Save Queue as Playlist <#save-queue-as-playlist>`__

      29. `Clear Queue <#clear-queue>`__

      30. `Play Next <#play-next>`__

      31. `Play Previous <#play-previous>`__

   6. `Group Commands <#group-commands>`__

      32. `Get Groups <#get-groups>`__

      33. `Get Group Info <#get-group-info>`__

      34. `Set Group <#set-group>`__

      35. `Get Group Volume <#get-group-volume>`__

      36. `Set Group Volume <#set-group-volume>`__

      6. `Group Volume Up <#group-volume-up>`__

      7. `Group Volume Down <#group-volume-down>`__

      8.  `Get Group Mute <#get-group-mute>`__

      9.  `Set Group Mute <#set-group-mute>`__

      10. `Toggle Group Mute <#toggle-group-mute>`__

   3. `Browse Commands <#browse-commands>`__

      1.  `Get Music Sources <#get-music-sources>`__

      2.  `Get Source Info <#get-source-info>`__

      3.  `Browse Source <#browse-source>`__

      4.  `Browse Source Containers <#browse-source-containers>`__

      5.  `Get Source Search Criteria <#get-source-search-criteria>`__

      6.  `Search <#search>`__

      7.  `Play Station <#_bookmark58>`__

      8.  `Play Input source <#_bookmark59>`__

      9.  `Add Container to Queue with
          Options <#add-container-to-queue-with-options>`__

      10. `Add Track to Queue with
          Options <#add-track-to-queue-with-options>`__

      11. `Get HEOS Playlists <#get-heos-playlists>`__

      12. `Rename HEOS Playlist <#rename-heos-playlist>`__

      13. `Delete HEOS Playlist <#delete-heos-playlist>`__

      14. `Get HEOS History <#get-heos-history>`__

      15. `Retrieve Album Metadata <#retrieve-album-metadata>`__

      16. `Get Service Options for now playing screen -
          OBSOLETE <#get-service-options-for-now-playing-screen---obsolete>`__

      17. `Set service option <#set-service-option>`__

5. `Change Events (Unsolicited
   Responses) <#change-events-unsolicited-responses>`__

   7.  `Sources Changed <#sources-changed>`__

   8.  `Players Changed <#players-changed>`__

   9.  `Group Changed <#group-changed>`__

   10. `Source Data Changed <#source-data-changed>`__

   11. `Player State Changed <#player-state-changed>`__

   12. `Player Now Playing Changed <#player-now-playing-changed>`__

   13. `Player Now Playing Progress <#player-now-playing-progress>`__

   14. `Player Playback Error <#player-playback-error>`__

   15. `Player Queue Changed <#player-queue-changed>`__

   16. `Player Volume Changed <#player-volume-changed>`__

   17. `Player Mute Changed <#player-mute-changed>`__

   18. `Player Repeat Mode Changed <#player-repeat-mode-changed>`__

   19. `Player Shuffle Mode Changed <#player-shuffle-mode-changed>`__

   20. `Group Status Changed <#_bookmark83>`__

   21. `Group Volume Changed <#group-volume-changed>`__

   22. `Group Mute Changed <#group-mute-changed>`__

   23. `User Changed <#user-changed>`__

   0. `Error Codes <#error-codes>`__

   1. `General Error Response <#general-error-response>`__

   2. `Error Code and Text Table <#error-code-and-text-table>`__

+-------------+-------------+-------------+-------------+-------------+
|    **Versio |    **HEOS   |    **Modifi |    **Date** |    **Author |
| n**         |    Version* | cations**   |             | **          |
|             | *           |             |             |             |
+=============+=============+=============+=============+=============+
|    1.0      |    1.280.96 |    Initial  |    12/20/20 |    Prakash  |
|             |             |    release  | 14          |    Mortha   |
+-------------+-------------+-------------+-------------+-------------+
|    1.1      |    1.304.61 |    Add set  |    05/27/20 |    Prakash  |
|             |             |    service  | 15          |    Mortha   |
|             |             |    option   |             |             |
|             |             |    command  |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    1.2      |    1.310.17 |    Remove   |    08/06/20 |    Prakash  |
|             | 0           |    support  | 15          |    Mortha   |
|             |             |    for play |             |             |
|             |             |    url      |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    1.3      |    TBD      |    Add      |    TDB      |    Prakash  |
|             |             |    reboot   |             |    Mortha   |
|             |             |    command  |             |             |
+-------------+-------------+-------------+-------------+-------------+

Overview
========

   The Denon HEOS is a network connected, wireless, multi-room music
   system. The HEOS Command Line Interface (CLI) allows external control
   systems to manage, browse, play, and get status from the Denon HEOS
   products. The HEOS CLI is accessed through a telnet connection
   between the HEOS product and the control system. The control system
   sends commands and receives responses over the network connection.
   The CLI commands and responses are in human readable (ascii) format.
   The command is a text string and the responses are in JSON format.
   The commands and responses for browsing music servers and services
   use a RESTFUL like approach while other commands and responses are
   more static.

Connection
==========

   The HEOS products can be discovered using the UPnP SSDP protocol.
   Through discovery, the IP address of the HEOS products can be
   retrieved. Once the IP address is retrieved, a telnet connection to
   port 1255 can be opened to access the HEOS CLI and control the HEOS
   system. The HEOS product IP address can also be set statically and
   manually programmed into the control system. Search target name (ST)
   in M-SEARCH discovery request is
   'urn:schemas-denon-com:device:ACT-Denon:1'.

   The control system should use various Get commands to determine the
   players and groups currently in the HEOS system.

   Controller software can control all HEOS speakers in the network by
   establishing socket connection with just one HEOS speaker. It

   is recommended not to establish socket connection to each HEOS
   speaker. This is to decrease network traffic caused by establishing
   socket connection to each HEOS speaker. Controller software can open
   multiple socket connections to the single HEOS speaker. Typically
   controllers will use one connection to listen for change events and
   one to handle user actions.

1. .. rubric:: Controller Design Guidelines
      :name: controller-design-guidelines

   1. .. rubric:: Driver Initialization
         :name: driver-initialization

..

   In order to reduce number of UPnP devices running on the network,
   HEOS Speaker runs CLI module in a dormant mode. HEOS speaker spawns
   CLI core modules when the controller establishes the first socket
   connection to the speaker. What it all means for controller?

   Inability of CLI module to process player commands. This is because,
   by nature of UPnP, CLI module need some time to discover all

   players before they can be identified by their unique Id (pid)

   Spew of events when controller initially connects to the speaker. In
   order to avoid excessive event handling in a event driven controller
   system, the following initialization sequence is suggested:

1. Un-register for change events. By default speaker doesn't send
   unsolicited events but still it is a good idea to send un-register
   command.This is done through 'register_for_change_events' command.

2. If user credentials are available, sign-in to HEOS user account. This
   is done through 'sign_in' command.

3. Retrieve current HEOS ecosystem status. This is done through commands
   like 'get_players', 'get_sources', 'get_groups', 'get_queue',
   'get_now_playing_media', 'get_volume', 'get_play_state' etc.

4. Register for change events. This is done through
   'register_for_change_events' command.

..

   If controller design involves disconnect and reconnect to HEOS
   speakers through CLI, it is recommended to keep a idle connection to
   HEOS Speaker thus avoiding CLI module to set back to dormant mode.

Caveats
~~~~~~~

   Please take a look at the following suggestions to avoid breaking
   controller code due to future enhancements

   The 'message' field part of HEOS response is a string. The attribute
   value pair in this message string is delimited by '&'. Further the
   attribute name and value is separated by '=' sign. Please note that
   new arguments can be added in the future.

   New JSON objects may be added to the 'payload' as part of future
   enhancements.

Miscellaneous
~~~~~~~~~~~~~

   Controllers can add custom argument SEQUENCE=<number> in browse
   commands to associate command and response. This is possible because
   the 'message' field in the response packet includes all the arguments
   sent in the command. Please let us know if you need additional custom
   argument other than 'SEQUENCE'. This is to avoid accidentally using
   HEOS command arguments for special purpose.

   Maximum number of simultaneous socket connections supported by HEOS
   speaker is 32.

3. .. rubric:: Command and Response Overview
      :name: command-and-response-overview

   2. .. rubric:: Commands
         :name: commands

..

   HEOS CLI commands are in the following general format:
   heos://command_group/command?attribute1=value1&attribute2=value2&…&attributeN=valueN

   Command string delimiter is "\r\n".

Responses
---------

   The responses to commands are in JSON format and use the following
   general structure:

   {

"heos": {

},

   "command": "'command_group'/'command'", "result": "'success' or
   'fail'",

   "message": "other result information'"

"payload":{

}

   }

   'Rest of response data'

   Some command responses will not include a payload.

   If the "result" of the command is "fail" then the "message"
   information contains the error codes for the failure. The error codes
   can be found in Section TBD.

   Some commands will also cause unsolicited responses. For example,
   sending the 'player/clear_queue' command will also cause the
   Player/Group Queue Changed response and could also cause the
   Player/Group Status Changed response.

   When the actual response can't be populated immediately, a special
   response will be sent back as shown below. This usually occurs during
   browse/search as CLI needs to retrieve data from remote media server
   or online service.

   {

"heos": {

}

   }

   "command": "'command_group'/'command'", "result": "'success'",

   "message": "command under process'"

   JSON command response delimiter is "\r\n".

4. .. rubric:: Command and Response Details
      :name: command-and-response-details

   4. .. rubric:: System Commands
         :name: system-commands

      4. .. rubric:: Register for Change Events
            :name: register-for-change-events

..

   By default HEOS speaker does not send Change events. Controller needs
   to send this command with enable=on when it is ready to receive
   unsolicit responses from CLI. Please refer to "Driver Initialization"
   section regarding when to register for change events.

   Command: heos://system/register_for_change_events?enable='on_or_off'

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    enable    | Register or unregister for change events. | on,off      |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "system/register_for_change_events", "result": "success",

   "message": "enable='on_or_off'"

   Example: heos://system/register_for_change_events?enable=on

HEOS Account Check
~~~~~~~~~~~~~~~~~~

   Command: heos://system/check_account

   This command returns current user name in its message field if the
   user is currently singed in. Response:

   {

"heos": {

}

   }

   "command": "system/check_account", "result": "success",

   "message": "signed_out" or "signed_in&un=<current user name>"

   Example: heos://system/check_account

HEOS Account Sign In
~~~~~~~~~~~~~~~~~~~~

   Command: heos://system/sign_in?un=heos_username&pw=heos_password

+--------------+-----------------------+-------------+
|    Attribute | Description           | Enumeration |
+==============+=======================+=============+
|    un        | HEOS account username | N/A         |
+--------------+-----------------------+-------------+
|    pw        | HEOS account password | N/A         |
+--------------+-----------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "system/sign_in ", "result": "success",

   "message": "signed_in&un=<current user name>"

   Example: heos://system/sign_in?un=user@gmail.com&pw=12345

HEOS Account Sign Out
~~~~~~~~~~~~~~~~~~~~~

   Command: heos://system/sign_out Response:

   {

"heos": {

}

   }

   "command": "system/sign_out ", "result": "success",

   "message": "signed_out"

   Example: heos://system/sign_out

HEOS System Heart Beat
~~~~~~~~~~~~~~~~~~~~~~

   Command: heos://system/heart_beat Response:

   {

"heos": {

}

   }

   "command": "system/heart_beat ", "result": "success"

   "message": ""

   Example: heos://system/heart_beat

HEOS Speaker Reboot
~~~~~~~~~~~~~~~~~~~

   Using this command controllers can reboot HEOS device. This command
   can only be used to reboot the HEOS device to which the controller is
   connected through CLI port.

   Command: heos://system/reboot Response:

   {

"heos": {

}

   }

   "command": "system/reboot", "result": "success" "message": ""

   Example: heos://system/reboot

Prettify JSON response
~~~~~~~~~~~~~~~~~~~~~~

   Helper command to prettify JSON response when user is running CLI
   controller through telnet. Command:
   heos://system/prettify_json_response?enable='on_or_off'

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    enable             | Enable or disable     | on,off                |
|                       | prettification of     |                       |
|                       | JSON response.        |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

   "heos": {

   "command": "system/prettify_json_response", "result": "success",

   "message": "enable='on_or_off'"

   }

   }

   Example: heos://system/prettify_json_response?enable=on

2. .. rubric:: Player Commands
      :name: player-commands

   1. .. rubric:: Get Players
         :name: get-players

..

   Command: heos://player/get_players

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           |    Enumeration        |
+=======================+=======================+=======================+
|    pid                | Player id             |    N/A                |
+-----------------------+-----------------------+-----------------------+
|    gid                | pid of the Group      |    N/A                |
|                       | leader                |                       |
+-----------------------+-----------------------+-----------------------+
|    lineout            | LineOut level type    | 1. - variable         |
|                       |                       |                       |
|                       |                       | 2. - Fixed            |
+-----------------------+-----------------------+-----------------------+
|    control            | Only valid when       | 1. - None             |
|                       | lintout level type is |                       |
|                       | Fixed (2).            | 2. - IR               |
|                       |                       |                       |
|                       |                       | 3. - Trigger          |
|                       |                       |                       |
|                       |                       | 4. - Network          |
+-----------------------+-----------------------+-----------------------+

..

   Note: The group id field (gid) is optional. The 'gid' field will only
   be appeared if the player(s) is part of a group. Note: control field
   is only populated when lineout level type is Fixed (lineout = 2)

   Response::
   
      {
         "heos": {
            "command": "player/get_players", 
            "result": "success",
            "message": ""
          },

        "payload": [
            {
               "name": "'player name 1'",
               "pid": "player id 1'",
               "gid": "group id'",
               "model": "'player model 1'",
               "version": "'player verison 1'"
               "lineout": "level type" 
               "control": "control option"
            }, ...]
       }

   Example: heos://player/get_players

Get Player Info
~~~~~~~~~~~~~~~

   Command: heos://player/get_player_info?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    gid                | pid of the Group      | N/A                   |
|                       | leader                |                       |
+-----------------------+-----------------------+-----------------------+
|    lineout            | LineOut level type    | 1. - variable         |
|                       |                       |                       |
|                       |                       | 2. - Fixed            |
+-----------------------+-----------------------+-----------------------+
|    control            | Only valid when       | 1. - None             |
|                       | lintout level type is |                       |
|                       | Fixed (2).            | 2. - IR               |
|                       |                       |                       |
|                       |                       | 3. - Trigger          |
|                       |                       |                       |
|                       |                       | 4. - Network          |
+-----------------------+-----------------------+-----------------------+

..

   Note: The group id field (gid) is optional. The 'gid' field will only
   be appeared if the player(s) is part of a group. Note: control field
   is only populated when lineout level type is Fixed (lineout = 2)

   Response:

   {

"heos": {

},

   "command": "player/get_player_info", "result": "success",

   "message": "pid='player_id'"

"payload": {

}

   }

   "name": "'player name'",

   "pid": "player id'",

   "gid": "group id'",

   "model": "'player model'", "version": "'player verison'" "lineout":
   "level type" "control": "control option"

   Example: heos://player/get_player_info?pid=1

Get Play State
~~~~~~~~~~~~~~

   Command: heos://player/get_play_state?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/get_play_state ", "result": "success",

   "message": "pid='player_id'&state='play_state'"

   Example: heos://player/get_playe_state?pid=1

Set Play State
~~~~~~~~~~~~~~

   Command: heos://player/set_play_state?pid=player_id&state=play_state

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    state              | Player play state     | play, pause, stop     |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/set_play_state ", "result": "success",

   "message": "pid='player_id'&state='play_state'"

   Example: heos://player/set_play_state?pid=1&state=play

Get Now Playing Media
~~~~~~~~~~~~~~~~~~~~~

   Command: heos://player/get_now_playing_media?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    id (options)       | Options available for | Following options are |
|                       | now playing media     | currently supported   |
|                       |                       | for now playing media |
|                       |                       |                       |
|                       |                       |    11 - Thumbs Up     |
|                       |                       |    (Pandora) 12 -     |
|                       |                       |    Thumbs Down        |
|                       |                       |    (Pandora)          |
|                       |                       |                       |
|                       |                       |    19 - Add station   |
|                       |                       |    to HEOS Favorites  |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   The following response provides example when the speaker is playing a
   song.

   **Note:** For local music and DLNA servers sid will point to Local
   Music Source id.

   {

"heos": {

},

   "command": "player/get_now_playing_media", "result": "success",

   "message": "pid='player_id'"

"payload": {

}

   }

   "type" : "'song'",

   "song": "'song name'",

   "album": "'album name'",

   "artist": "'artist name'",

   "image_url": "'image url'",

   "mid": "'media id'",

   "qid": "'queue id'", "sid": source_id

   "album_id": "Album Id'"

   The following response provides example when the speaker is playing a
   station.

   {

   "heos": {

   "command": "player/get_now_playing_media", "result": "success",

   "message": "pid='player_id'"

   },

"payload": {

}

"options": [

   "type" : "'station'",

   "song": "'song name'",

   "station": "'station name'",

   "album": "'album name'",

   "artist": "'artist name'",

   "image_url": "'image url'",

   "mid": "'media id'",

   "qid": "'queue id'", "sid": source_id

   {

   "play": [

{

}

]

   }

]

   }

   "id": 19,

   "name": "Add to HEOS Favorites"

   Example: heos://player/get_now_playing_media?pid=1

Get Volume
~~~~~~~~~~

   Command: heos://player/get_volume?pid='player_id'

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ get_volume ", "result": "success",

   "message": "pid='player_id'&level='vol_level'"

   Example: heos://player/get_volume?pid=1

Set Volume
~~~~~~~~~~

   Command: heos://player/set_volume?pid=player_id&level=vol_level

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    level              | Player volume level   | 0 to 100              |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ set_volume ", "result": "success",

   "message": "pid='player_id'&level='vol_level'"

   Example: heos://player/set_volume?pid=2&level=30

Volume Up
~~~~~~~~~

   Command: heos://player/volume_up?pid=player_id&step=step_level

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    step               | Player volume step    | 1 to 10(default 5)    |
|                       | level                 |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ volume_up ", "result": "success",

   "message": "pid='player_id'&step='step_level'"

   Example: heos://player/volume_up?pid=2&step=5

Volume Down
~~~~~~~~~~~

   Command: heos://player/volume_down?pid=player_id&step=step_level

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    level              | Player volume step    | 1 to 10(default 5)    |
|                       | level                 |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ volume_down ", "result": "success",

   "message": "pid='player_id'&step='step_level'"

   Example: heos://player/volume_down?pid=2&step=5

Get Mute
~~~~~~~~

   Command: heos://player/get_mute?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ get_mute ", "result": "success",

   "message": "pid='player_id'&state='on_or_off'"

   Example: heos://player/get_mute?pid=1

Set Mute
~~~~~~~~

   Command: heos://player/set_mute?pid=player_id&state=on_or_off

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    state              | Player mute state     | on, off               |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ set_mute ", "result": "success",

   "message": "pid='player_id'&state='on_or_off'"

   Example: heos://player/set_mute?pid=3&state=off

Toggle Mute
~~~~~~~~~~~

   Command: heos://player/toggle_mute?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/ toggle_mute ", "result": "success",

   "message": "pid=player_id"

   Example: heos://player/toggle_mute?pid=3

Get Play Mode
~~~~~~~~~~~~~

   Command: heos://player/get_play_mode?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/get_play_mode", "result": "success",

   "message": "pid='player_id'&&repeat=
   *on_all*\ \_or\_\ *on_one*\ \_or\_\ *off*\ &shuffle=\ *on*\ \_or\_\ *off*"

   Example: hoes://player/get_play_mode?pid=1

Set Play Mode
~~~~~~~~~~~~~

   Command:
   heos://player/set_play_mode?pid='player_id'&repeat=\ *on_all*\ \_or\_\ *on_one*\ \_or\_\ *off*\ &shuffle=\ *on*\ \_or\_\ *off*

+-----------------------+-----------------------+-----------------------+
| Attribute             | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    repeat             | Player repeat state   | *on_all, on_one*,     |
|                       |                       | *off*                 |
+-----------------------+-----------------------+-----------------------+
|    shuffle            | Player shuffle state  | *on, off*             |
+-----------------------+-----------------------+-----------------------+
| Response:             |                       |                       |
+-----------------------+-----------------------+-----------------------+
| {                     |                       |                       |
+-----------------------+-----------------------+-----------------------+
| "heos":               | {                     |                       |
+-----------------------+-----------------------+-----------------------+
|                       |    "command": "       |                       |
|                       |    player/set_play_mo |                       |
|                       | de",                  |                       |
+-----------------------+-----------------------+-----------------------+
|                       |    "result":          |                       |
|                       |    "success",         |                       |
+-----------------------+-----------------------+-----------------------+

..

   "message": "pid='player_id'&repeat=
   *on_all*\ \_or\_\ *on_one*\ \_or\_\ *off*\ &shuffle=\ *on_or_off*"

   }

   }

   Example: heos://player/set_play_mode?pid=1&repeat=on_all&shuffle=off

Get Queue
~~~~~~~~~

   Command: heos://player/get_queue?pid=player_id&range=start#, end#

   Range is start and end record index to return. Range parameter is
   optional. Omitting range parameter returns all records but a maximum
   of 100 records are returned per response.

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    range              | Range is start and    | range starts from 0   |
|                       | end record index to   |                       |
|                       | return. Range         |                       |
|                       | parameter is          |                       |
|                       | optional.             |                       |
+-----------------------+-----------------------+-----------------------+
|                       | Omitting range        |                       |
|                       | parameter returns all |                       |
|                       | records up to a       |                       |
|                       | maximum of 100        |                       |
|                       | records per response. |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

},

   "command": "player/get_queue", "result": "success",

   "message": "'pid=player_id&range=start#, end#"

   "payload": [

{

},

{

},

.

   "song": "'song name 1'",

   "album": "'album name 1'",

   "artist": "'artist name 1'", "image_url": "'image_url 1'", "qid":
   "'queue id 1'",

   "mid": "'media id 1'" "album_id": "AlbumId 1'"

   "song": "'song name 2'",

   "album": "'album name 2'",

   "artist": "'artist name 2'",

   " image_url": "''image_url 2'",

   "qid": "'queue id 2'",

   "mid": "'media id 2'" "album_id": "AlbumId 2'"

   .

   .

   {

   "song": "'song name N'",

   "album": "'album name N'",

   "artist": "'artist name N'",

   " image_url": "''image_url N'",

   "qid": "'queue id N'",

   "mid": "'media id N'"

   "album_id": "AlbumId N'"

   }

   ]

   }

   Example: heos://player/get_queue?pid=1&range=0,10

Play Queue Item
~~~~~~~~~~~~~~~

   Command: heos://player/play_queue?pid=player_id&qid=queue_song_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    qid                | Queue id for song     | N/A                   |
|                       | returned by           |                       |
|                       | 'get_queue' command   |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/play_queue", "result": "success",

   "message": "pid='player_id'&qid='queue_id'"

   Example: heos://player/play_queue?pid=2&qid=9

Remove Item(s) from Queue
~~~~~~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://player/remove_from_queue?pid=player_id&qid=queue_id_1,queue_id_2,…,queue_id_n

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    qid                | List of comma         | N/A                   |
|                       | separated queue_id's  |                       |
|                       | where each queue id   |                       |
|                       | for song is returned  |                       |
|                       | by 'get_queue'        |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "player/remove_from_queue ", "result": "success",

   "message": "pid='player_id'&qid=queue_id_1, queue_id_2,…,queue_id_n'"

   Example: heos://player/remove_from_queue? pid=1&qid=4,5,6

Save Queue as Playlist
~~~~~~~~~~~~~~~~~~~~~~

   Command: heos://player/save_queue?pid=player_id&name=playlist_name

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    name               | String for new        | N/A                   |
|                       | playlist name limited |                       |
|                       | to 128 unicode        |                       |
|                       | characters            |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "player/save_queue ", "result": "success",

   "message": "pid='player_id'&name='playlist_name'"

   Example: heos://player/save_queue?pid=1&name=great playlist

Clear Queue
~~~~~~~~~~~

   Command: heos://player/clear_queue?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "player/clear_queue ", "result": "success",

   "message": "pid='player_id'"

   Example: heos://player/clear_queue

Play Next
~~~~~~~~~

   Command: heos://player/play_next?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/play_next", "result": "success",

   "message": "pid=player_id"

   Example: heos://player/play_next?pid=1

Play Previous
~~~~~~~~~~~~~

   Command: heos://player/play_previous?pid=player_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " player/play_previous", "result": "success",

   "message": "pid=player_id"

   Example: heos://player/play_previous?pid=1

3. .. rubric:: Group Commands
      :name: group-commands

   1. .. rubric:: Get Groups
         :name: get-groups

..

   Command: heos://group/get_groups Response:

   {

"heos": {

},

   "command": "player/get_groups", "result": "success",

   "message": ""

   "payload": [

{

   "name": "'group name 1'",

   "gid": "group id 1'", "players": [

   {

   "name": "player name 1", "pid": "'player id 1'",

   "role": "player role 1 (leader or member)'"

   },

   {

   "name": "player name 2", "pid": "'player id 2'",

   "role": "player role 2 (leader or member)'"

   },

   .

   .

   .

   {

   "name": "player name N", "pid": "'player id N'",

   "role": "player role N (leader or member)'"

   }

   ]

   },

   {

   "name": "'group name 2'",

   "gid": "group id 2'", "players": [

   {

   "name": "player name 1", "pid": "'player id 1'",

   "role": "player role 1 (leader or member)'"

   },

   {

   "name": "player name 2", "pid": "'player id 2'",

   "role": "player role 2 (leader or member)'"

   },

   .

   .

   .

   {

   "name": "player name N", "pid": "'player id N'",

   "role": "player role N (leader or member)'"

   }

   ]

   },

   .

   .

   .

   {

   "name": "'group name N'",

   "gid": "group id N'", "players": [

   {

   "name": "player name 1", "pid": "'player id 1'",

   "role": "player role 1 (leader or member)'"

   },

   {

   "name": "player name 2", "pid": "'player id 2'",

   "role": "player role 2 (leader or member)'"

   },

   .

   .

   .

   {

   "name": "player name N", "pid": "'player id N'",

   "role": "player role N (leader or member)'"

   }

   ]

   }

   ]

   }

   Example: heos://group/get_groups

Get Group Info
~~~~~~~~~~~~~~

   Command: heos://group/get_group_info?gid=group_id

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

},

   "command": "player/get_groups", "result": "success",

   "message": "gid=group_id"

   "payload": {

   "name": "'group name 1'",

   "gid": "group id 1'", "players": [

   {

   "name": "player name 1", "pid": "'player id 1'",

   "role": "player role 1 (leader or member)'"

   },

   {

   "name": "player name 2", "pid": "'player id 2'",

   "role": "player role 2 (leader or member)'"

   },

   .

   .

   .

   {

   "name": "player name N",

   "pid": "'player id N'",

   "role": "player role N (leader or member)'"

   }

   ]

   }

   }

   Example: heos://group/get_group_info&?gid=1

Set Group
~~~~~~~~~

   This command is used to perform the following actions: Create new
   group:

   Creates new group. First player id in the list is group leader. Ex:
   heos://group/set_group?pid=3,1,4

   Modify existing group members:

   Adds or delete players from the group. First player id should be the
   group leader id. Ex: heos://group/set_group?pid=3,1,5

   Ungroup all players in the group

   Ungroup players. Player id (pid) should be the group leader id. Ex:
   heos://group/set_group?pid=3

   Command: heos://group/set_group?pid=player_id_leader,
   player_id_member_1,…,player_id_member_n

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    pid                | List of comma         | N/A                   |
|                       | separated player_id's |                       |
|                       | where each player id  |                       |
|                       | is returned by        |                       |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command; |                       |
|                       | first player_id in    |                       |
|                       | list is group leader  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   The following response provides example when a group is
   created/modified.

   {

"heos": {

}

   }

   "command": "player/set_group ", "result": "success",

   "message": "gid='new group_id'&name='group_name'&pid='player_id_1,
   player_id_2,…,player_id_n'

   The following response provides example when all the speakers in the
   group are un-grouped.

   {

"heos": {

}

   }

   "command": "player/set_group ", "result": "success",

   "message": "pid='player_id'

   Example: heos://group/set_group?pid=3,1,4

Get Group Volume
~~~~~~~~~~~~~~~~

   Command: heos://group/get_volume?gid=group_id

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "group/get_volume ", "result": "success",

   "message": "gid='group_id'&level='vol_level'"

   Example: heos://group/get_volume?gid=1

Set Group Volume
~~~~~~~~~~~~~~~~

   Command: heos://group/set_volume?gid=group_id&level=vol_level

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+
|    level     | Group volume level                        | 0 to 100    |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "group/set_volume ", "result": "success",

   "message": "gid='group_id'&level='vol_level'"

   Example: heos://group/set_volume?gid=1&level=30

Group Volume Up
~~~~~~~~~~~~~~~

   Command: heos://group/volume_up?gid=group_id&step=step_level

+--------------+-------------------------------------------+--------------------+
|    Attribute | Description                               | Enumeration        |
+==============+===========================================+====================+
|    gid       | Group id returned by 'get_groups' command | N/A                |
+--------------+-------------------------------------------+--------------------+
|    step      | Group volume step level                   | 1 to 10(default 5) |
+--------------+-------------------------------------------+--------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " group/ volume_up ", "result": "success",

   "message": "gid='group_id'&step='step_level'"

   Example: heos://group/volume_up?gid=1&step=5

Group Volume Down
~~~~~~~~~~~~~~~~~

   Command: heos://group/volume_down?gid=group_id&step=step_level

+--------------+-------------------------------------------+--------------------+
|    Attribute | Description                               | Enumeration        |
+==============+===========================================+====================+
|    gid       | Group id returned by 'get_groups' command | N/A                |
+--------------+-------------------------------------------+--------------------+
|    level     | Group volume step level                   | 1 to 10(default 5) |
+--------------+-------------------------------------------+--------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": " group/ volume_down ", "result": "success",

   "message": "gid='group_id'&step='step_level'"

   Example: heos://group/volume_down?gid=1&step=5

Get Group Mute
~~~~~~~~~~~~~~

   Command: heos://group/get_mute?gid=group_id

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "group/ get_mute ", "result": "success",

   "message": "gid='group_id'&state='on_or_off'"

   Example: heos://group/get_mute?gid=1

Set Group Mute
~~~~~~~~~~~~~~

   Command: heos://group/set_mute?gid=group_id&state=on_or_off

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+
|    state     | Group mute state                          | on, off     |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "group/ set_mute ", "result": "success",

   "message": "gid=group_id'&state='on_or_off'"

   Example: heos://group/set_mute?gid=1&state=off

Toggle Group Mute
~~~~~~~~~~~~~~~~~

   Command: heos://group/toggle_mute?gid=group_id

+--------------+-------------------------------------------+-------------+
|    Attribute | Description                               | Enumeration |
+==============+===========================================+=============+
|    gid       | Group id returned by 'get_groups' command | N/A         |
+--------------+-------------------------------------------+-------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "group/ toggle_mute ", "result": "success",

   "message": "gid=group_id"

   Example: heos://group/toggle_mute?gid=1

4. .. rubric:: Browse Commands
      :name: browse-commands

   1. .. rubric:: Get Music Sources
         :name: get-music-sources

..

   Command: heos://browse/get_music_sources Response:

   {

   "heos": {

   },

   "command": "browse/get_music_sources", "result": "success",

   "message": ""

   "payload": [

{

   "name": "source name 1", "image_url": "source logo url 1", "type":
   "source type 1",

   "sid": source_id_1

   },

   {

   "name": "source name 2", "image_url": "source logo url 2", "type":
   "source type 2",

   "sid": source_id_2

   },

   {

   "name": "source name N", "image_url": "source logo url N", "type":
   "source type N",

   "sid": source_id_N

   }

   ]

   }

   Example: heos://browse/get_music_sources

   The following are valid source types:

   music_service heos_service heos_server dlna_server

Get Source Info
~~~~~~~~~~~~~~~

   Command: heos://browse/get_source_info?sid=source_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           |    Enumeration        |
+=======================+=======================+=======================+
|    sid                | Source id returned by |    N/A                |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
|                       |                       |                       |
|                       | (Or) Source id        |                       |
|                       | returned by 'browse'  |                       |
|                       | command when browsing |                       |
|                       | source types          |                       |
|                       | 'heos_server' and     |                       |
|                       | 'heos_service'        |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

   "heos": {

   },

   "command": "browse/get_source_info", "result": "success",

   "message": ""

"payload": [

{

},

]

   }

   "name": "source name", "image_url": "source logo url", "type":
   "source type",

   "sid": source_id

   Example: heos://browse/get_source_info The following are valid source
   types:

   music_service heos_service heos_server dlna_server

Browse Source
~~~~~~~~~~~~~

   Command: heos://browse/browse?sid=source_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          |    Description        |    Enumeration        |
+=======================+=======================+=======================+
|    sid                |    Source id returned |    N/A                |
|                       |    by                 |                       |
|                       |    'get_music_sources |                       |
|                       | '                     |                       |
|                       |    command            |                       |
+-----------------------+-----------------------+-----------------------+
|                       |    (Or) Source id     |                       |
|                       |    returned by        |                       |
|                       |    'browse' command   |                       |
|                       |    when browsing      |                       |
|                       |    source             |                       |
+-----------------------+-----------------------+-----------------------+
|                       |    types              |                       |
|                       |    'heos_server' and  |                       |
|                       |    'heos_service'     |                       |
+-----------------------+-----------------------+-----------------------+
|    id                 |    Options available  |    Following options  |
|                       |    for current browse |    are currently      |
|                       |    level              |    supported for      |
|                       |                       |    'Browse Source'    |
|                       |                       |    command            |
|                       |                       |                       |
|                       |                       |    13 - Create New    |
|                       |                       |    Station (Pandora)  |
|                       |                       |                       |
|                       |                       |    20 - Remove from   |
|                       |                       |    HEOS Favorites     |
|                       |                       |    (Favorites)        |
+-----------------------+-----------------------+-----------------------+
|    (options)          |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    range              |    Range is start and |    range starts from  |
|                       |    end record index   |    0                  |
|                       |    to return. Range   |                       |
|                       |    parameter is       |    NOTE: Range in     |
|                       |    optional.          |    Browse source      |
|                       |                       |    command is only    |
|                       |    Omitting range     |    supported while    |
|                       |    parameter returns  |    browsing Favorites |
|                       |    all records up to  |                       |
|                       |    a maximum of       |                       |
|                       |    either 50 or 100   |                       |
|                       |    records per        |                       |
|                       |    response.          |                       |
|                       |                       |                       |
|                       |    The default        |                       |
|                       |    maximum number of  |                       |
|                       |    records depend on  |                       |
|                       |    the service type.  |                       |
+-----------------------+-----------------------+-----------------------+

..

   This command is used under two scenarios.

   Browsing actual media sources of type 'heos_server' and
   'heos_service'.

   The command 'Get Music Sources' lists all music servers (type
   'heos_server') in the network under one virtual source called 'Local
   Music'.

   Other virtual source that represents all auxiliary inputs (type
   'heos_service') is 'AUX Input'. Browsing top music view.

   Results of this command depends on the music source selected.

   **Note**: Optionally this command returns service 'options' that are
   available for current browse items. Please refer to 'Get Service
   Options for now playing screen' for service options available on now
   playing screen.

   **Note**: The following response provides examples of the various
   service options. The actual response will depend on the service
   options available for a given source type.

   Response while browsing actual media sources of type 'heos_server'
   and 'heos_service'. These includes 'Local Music', 'History', 'AUX
   Inputs', 'Playlists', and 'Favorites'.

   {

   "heos": {

   "command": "browse/browse", "result": "success",

   "message":
   "sid=source_id&returned=items_in_current_response&count=total_items_available"

   },

"payload": [

{

},

{

},

{

}

],

"options": [

{

   "name": "'source name 1'", "'image_url": "'source logo url 1'",
   "sid": "source id 1'",

   "type": "'source type 1'"

   "name": "'source name 2'", "'image_url": "'source logo url 2'",
   "sid": "source id 2'",

   "type": "'source type 2'"

   "name": "'source name N'", "'image_url": "'source logo url N'",
   "sid": "source id N'",

   "type": "'source type N'"

   "browse": [

   {

   "id": 13,

   "name": "create new station"

   }

   ]

   }

   ]

   }

   Example: heos://browse/browse?sid=1

   Response when browsing top music view in an actual music server/music
   services.

   **Note**: the following response provides examples of the various
   media types. The actual response will depend on the source browsed
   and the hierarchy supported by that source.

   {

   "heos": {

   },

   "command": "browse/browse", "result": "success",

   "message":
   "sid=source_id&returned=items_in_current_response&count=total_items_available"

   "payload": [

{

},

{

},

{

   "container": "yes",

   "playable": "no",

   "type": "artist",

   "name": "'artist name'", "image_url": "'artist image url'", "cid":
   "container id'",

   "mid": "media id"

   "container": "yes",

   "playable": "yes",

   "type": "album",

   "name": "'album name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "cid": "'container id'",

   "mid": "'media id'"

   "container": "no",

   "playable": "yes",

   "type": "song",

   "name": "'song name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "album": "'album name'",

   "mid": "'media id'"

   },

   {

   "container": "yes",

   "playable": "no",

   "type": "container",

   "name": "'container name'", "image_url": "'container image url'",
   "cid": "'container id'",

   "mid": "'media id'"

   },

   {

   "container": "no",

   "playable": "yes",

   "type": "station",

   "name": "'station name'", "image_url": "'station url'", "mid":
   "'media id'"

   }

   ]

   }

   Example: heos://browse/browse?sid=1346442495

   Supported Sources: Local Media Servers, Playlists, History, Aux-In,
   Favorites, TuneIn, Pandora, Rhapsody, Deezer, SiriusXM, iHeartRadio,
   Napster

Browse Source Containers
~~~~~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://browse/browse?sid=source_id&cid=container_id&range=start#,
   end#

+-----------------------+-----------------------+-----------------------+
|    Attribute          |    Description        |    Enumeration        |
+=======================+=======================+=======================+
|    sid                |    Source id returned |    N/A                |
|                       |    by                 |                       |
|                       |    'get_music_sources |                       |
|                       | '                     |                       |
|                       |    command            |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                |    Container id       |    N/A                |
|                       |    returned by        |                       |
|                       |    'browse' or        |                       |
|                       |    'search' command   |                       |
+-----------------------+-----------------------+-----------------------+
|    range              |    Range is start and |    range starts from  |
|                       |    end record index   |    0                  |
|                       |    to return. Range   |                       |
|                       |    parameter is       |                       |
|                       |    optional. Omitting |                       |
|                       |    range parameter    |                       |
|                       |    returns all        |                       |
|                       |    records up to a    |                       |
|                       |    maximum of either  |                       |
|                       |    50 or 100 records  |                       |
|                       |    per response.      |                       |
|                       |                       |                       |
|                       |    The default        |                       |
|                       |    maximum number of  |                       |
|                       |    records depend on  |                       |
|                       |    the service type.  |                       |
+-----------------------+-----------------------+-----------------------+
|    count              |    Total number of    |    0 - unknown        |
|                       |    items available in |                       |
|                       |    the container.     |    >1 - valid count   |
|                       |                       |                       |
|                       |    NOTE: count value  |                       |
|                       |    of '0' indicates   |                       |
|                       |    unknown container  |                       |
|                       |    size. Controllers  |                       |
|                       |    needs to query     |                       |
|                       |    until the return   |                       |
|                       |    payload            |                       |
|                       |                       |                       |
|                       |    is empty (returned |                       |
|                       |    attribute is 0).   |                       |
+-----------------------+-----------------------+-----------------------+
|    returned           |    Number of items    |    N/A                |
|                       |    returned in        |                       |
|                       |    current response   |                       |
+-----------------------+-----------------------+-----------------------+
|    id (options)       |    Options available  |    Following options  |
|                       |    for current browse |    are currently      |
|                       |    level              |    supported for      |
|                       |                       |    'Browse Source     |
|                       |                       |    container'         |
|                       |                       |                       |
|                       |                       |    command:           |
|                       |                       |                       |
|                       |                       |    1 - Add Track to   |
|                       |                       |    Library (Rhapsody) |
|                       |                       |    2 - Add Album to   |
|                       |                       |    Library (Rhapsody) |
|                       |                       |    3 - Add Station to |
|                       |                       |    Library (Rhapsody) |
|                       |                       |    4 - Add Playlist   |
|                       |                       |    to Library         |
|                       |                       |    (Rhapsody)         |
|                       |                       |                       |
|                       |                       |    5 - Remove Track   |
|                       |                       |    from Library       |
|                       |                       |    (Rhapsody) 6 -     |
|                       |                       |    Remove Album from  |
|                       |                       |    Library (Rhapsody) |
|                       |                       |    7 - Remove Station |
|                       |                       |    from Library       |
|                       |                       |    (Rhapsody) 8 -     |
|                       |                       |    Remove Playlist    |
|                       |                       |    from Library       |
|                       |                       |    (Rhapsody) 13 -    |
|                       |                       |    Create New Station |
|                       |                       |    (Pandora)          |
+-----------------------+-----------------------+-----------------------+

..

   The following are valid media types: song

   station genre artist album container

   **Note:** A "yes" for the "container" field as well as the "playable"
   field implies that the container supports adding all media items to
   the play queue. Adding all media items of the container to the play
   queue is performed through `"Add containers to
   queue" <https://dm-confluence.atlassian.net/wiki/display/prod/Add%2BContainer%2Bto%2BQueue%2Bwith%2BOptions>`__\ command.

   **Note**: Following response provides examples of the various media
   types. The actual response will depend on the source browsed and the
   hierarchy supported by that source.

   Response:

   {

   "heos": {

   "command": "browse/browse", "result": "success", "message":

   "sid='source_id&cid='container_id'&range='start,end'&returned=items_in_current_response&count=total_items_available"

   },

   "payload": [

{

},

{

},

{

},

{

},

{

}

],

"options": [

{

   "container": "yes",

   "playable": "no",

   "type": "artist",

   "name": "'artist name'", "image_url": "'artist image url'", "cid":
   "container id'",

   "mid": "media id"

   "container": "yes",

   "playable": "yes",

   "type": "album",

   "name": "'album name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "cid": "'container id'",

   "mid": "'media id'"

   "container": "no",

   "playable": "yes",

   "type": "song",

   "name": "'song name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "album": "'album name'",

   "mid": "'media id'"

   "container": "yes",

   "playable": "no",

   "type": "container",

   "name": "'container name'", "image_url": "'container image url'",
   "cid": "'container id'",

   "mid": "'media id'"

   "container": "no",

   "playable": "yes",

   "type": "station",

   "name": "'station name'", "image_url": "'station url'", "mid":
   "'media id'"

   "browse": [

   {

   "id": 4,

   "name": "Add Playlist to Library"

   }

   ]

   }

   ]

   }

   Example: heos://browse/browse?sid=2&cid=TopAlbums&range=0,100

   Supported Sources: Local Media Servers, Playlists, History, Aux-In,
   TuneIn, Pandora, Rhapsody, Deezer, SiriusXM, iHeartRadio, Napster

Get Source Search Criteria
~~~~~~~~~~~~~~~~~~~~~~~~~~

   Command: heos://browse/get_search_criteria?sid=source_id

+--------------+---------------------------------------------------+-------------+
|    Attribute | Description                                       | Enumeration |
+==============+===================================================+=============+
|    sid       | Source id returned by 'get_music_sources' command | N/A         |
+--------------+---------------------------------------------------+-------------+

..

   **Note**: the following response provides examples of the various
   search criteria types. The actual response will depend on the source
   and the search types supported by that source.

   Response:

   {

"heos": {

},

   "command": "browse/ get_search_criteria ", "result": "success",

   "message": "sid='source_id "

"payload": [

{

},

{

},

{

},

{

}

   "name": "Artist",

   "scid": "'search_criteria_id'", "wildcard": "yes_or_no",

   "name": "Album",

   "scid": "'search_criteria_id'", "wildcard": "yes_or_no",

   "name": "Track",

   "scid": "'search_criteria_id'", "wildcard": "yes_or_no",

   "name": "Station",

   "scid": "'search_criteria_id'", "wildcard": "yes_or_no",

   ]

   }

   Example: heos://browse/get_search_criteria?sid=3

   Supported Sources: Local Media Servers, TuneIn, Rhapsody, Deezer,
   SiriusXM, Napster

Search
~~~~~~

   Command:
   heos://browse/search?sid=source_id&search=search_string&scid=search_criteria&range=start#,
   end#

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    search             | String for search     | N/A                   |
|                       | limited to 128        |                       |
|                       | unicode characters    |                       |
|                       | and may contain '*'   |                       |
|                       | for wildcard if       |                       |
|                       | supported by search   |                       |
+-----------------------+-----------------------+-----------------------+
|                       | criteria id           |                       |
+-----------------------+-----------------------+-----------------------+
|    scid               | Search criteria id    | artist, album, song,  |
|                       | returned by           | station               |
|                       | 'get_search_criteria' |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+

+-----------------------+-----------------------+-----------------------+
|    count              | Total number of items | 0 - unknown           |
|                       | available in the      |                       |
|                       | container.            | >1 - valid count      |
|                       |                       |                       |
|                       | NOTE: count value of  |                       |
|                       | '0' indicates unknown |                       |
|                       | container size.       |                       |
|                       | Controllers needs to  |                       |
|                       | query until the       |                       |
|                       | return payload        |                       |
|                       |                       |                       |
|                       | is empty (returned    |                       |
|                       | attribute is 0).      |                       |
+=======================+=======================+=======================+
|    range              | Range is start and    | range starts from 0   |
|                       | end record index to   |                       |
|                       | return. Range         |                       |
|                       | parameter is          |                       |
|                       | optional.             |                       |
|                       |                       |                       |
|                       | Omitting range        |                       |
|                       | parameter returns all |                       |
|                       | records up to a       |                       |
|                       | maximum of 50/100     |                       |
|                       | records per response. |                       |
|                       | The default maximum   |                       |
|                       | number of records     |                       |
|                       | depend on the service |                       |
|                       | type.                 |                       |
+-----------------------+-----------------------+-----------------------+
|    returned           | Number of items       | N/A                   |
|                       | returned in current   |                       |
|                       | response              |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   **Note**: the following response provides examples of the various
   media types. The actual response will depend on the source searched
   and the results returned for the search string.

   {

   "heos": {

   "command": "browse/search", "result": "success",

   "message": "sid='source_id&scid='search_criteria_id'&range='start#,

   end#'&returned=items_in_current_response&count='total_items_available"

   },

   "payload": [

   {

   "container": "yes",

   "playable": "no",

   "type": "artist",

   "name": "'artist name'", "image_url": "'artist image url'", "cid":
   "container id'",

   "mid": "media id"

   },

   {

   "container": "yes",

   "playable": "yes",

   "type": "album",

   "name": "'album name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "cid": "'container id'",

   "mid": "'media id'"

   },

   {

   "container": "no",

   "playable": "yes",

   "type": "song",

   "name": "'song name'", "image_url": "'album image url'", "artist":
   "'artist name'",

   "album": "'album name'",

   "mid": "'media id'"

   },

   {

   "container": "yes",

   "playable": "no",

   "type": "container",

   "name": "'container name'", "image_url": "'container image url'",
   "cid": "'container id'",

   "mid": "'media id'"

   },

   {

   "container": "no",

   "playable": "yes",

   "type": "station",

   "name": "'station name'", "image_url": "'station url'", "mid":
   "'media id'"

   }

   ]

+-----------------------+-----------------------+-----------------------+
| }                     |
|                       |
| Example:              |
| heos://browse/search? |
| sid=2&search="U2"&sci |
| d=1                   |
+=======================+=======================+=======================+
| Supported Sources:    |                       |                       |
| Local Media Servers,  |                       |                       |
| TuneIn, Rhapsody,     |                       |                       |
| Deezer, Napster       |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    **4.4.7 Play       |                       |                       |
|    Station**          |                       |                       |
+-----------------------+-----------------------+-----------------------+
| Command:              |                       |                       |
| heos://browse/play_st |                       |                       |
| ream?pid=player_id&si |                       |                       |
| d=source_id&cid=conta |                       |                       |
| iner_id&mid=media_id& |                       |                       |
| name=station_name     |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+-----------------------+-----------------------+-----------------------+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | N/A                   |
|                       | by 'browse' command.  |                       |
|                       | Ignore if container   |                       |
|                       | id doesn't exists as  |                       |
|                       | in case of playing    |                       |
|                       | station obtained      |                       |
|                       | through 'Search'      |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    mid                | Media id returned by  | N/A                   |
|                       | 'browse'or 'search'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    name               | Station name returned | N/A                   |
|                       | by 'browse' command.  |                       |
+-----------------------+-----------------------+-----------------------+
| Note: The mid for     |                       |                       |
| this command must be  |                       |                       |
| a 'station' media     |                       |                       |
| type. Response:       |                       |                       |
|                       |                       |                       |
| **Note**: this        |                       |                       |
| command will cause a  |                       |                       |
| Now Playing Change    |                       |                       |
| Event to occur if a   |                       |                       |
| new stream is played. |                       |                       |
|                       |                       |                       |
| {                     |                       |                       |
|                       |                       |                       |
|    "heos": {          |                       |                       |
|                       |                       |                       |
|    "command": "       |                       |                       |
|    browse/play_stream |                       |                       |
|    ", "result":       |                       |                       |
|    "success",         |                       |                       |
|                       |                       |                       |
|    "message":         |                       |                       |
|    "pid='player_id'&s |                       |                       |
| id='source_id&cid='co |                       |                       |
| ntainer_id'&mid='medi |                       |                       |
| a_id'&name='station_n |                       |                       |
| ame'"                 |                       |                       |
|                       |                       |                       |
|    }                  |                       |                       |
|                       |                       |                       |
| }                     |                       |                       |
|                       |                       |                       |
| Example:              |                       |                       |
| heos://browse/play_st |                       |                       |
| ream?pid=1&sid=2&cid= |                       |                       |
| 'CID-55'&mid=15376&na |                       |                       |
| me=Q95                |                       |                       |
+-----------------------+-----------------------+-----------------------+
| Supported Sources:    |                       |                       |
| History, Favorites,   |                       |                       |
| TuneIn, Pandora,      |                       |                       |
| Rhapsody, Deezer,     |                       |                       |
| SiriusXM,             |                       |                       |
| iHeartRadio, Napster  |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    **4.4.8 Play Input |                       |                       |
|    source**           |                       |                       |
+-----------------------+-----------------------+-----------------------+
| Command to play input |                       |                       |
| source on the same    |                       |                       |
| speaker:              |                       |                       |
+-----------------------+-----------------------+-----------------------+
| heos://browse/\ **pla |                       |                       |
| y_input**?\ **pid**\  |                       |                       |
| =player_id&\ **inpu** |                       |                       |
| \ t=input_name        |                       |                       |
+-----------------------+-----------------------+-----------------------+
| Command to play input |                       |                       |
| source on another     |                       |                       |
| speaker:              |                       |                       |
+-----------------------+-----------------------+-----------------------+
| heos://browse/\ **pla |                       |                       |
| y_input**?\ **pid**\  |                       |                       |
| =destination_player_i |                       |                       |
| d&\ **spid**\ =source |                       |                       |
| _player_id&\ **input* |                       |                       |
| *\ =input_name        |                       |                       |
+-----------------------+-----------------------+-----------------------+

..

   OBSOLETE command that requires sid:
   heos://browse/\ **play_stream**?\ **pid**\ =player_id&\ **sid**\ =source_id&\ **mid**\ =media
   id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    pid                | player id of the      | N/A                   |
|                       | selected speaker      |                       |
|                       | (destination HEOS     |                       |
|                       | speaker)              |                       |
+-----------------------+-----------------------+-----------------------+
|                       | Player id returned by |                       |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+
|    mid                | media id returned by  | N/A                   |
|                       | 'browse' command      |                       |
+-----------------------+-----------------------+-----------------------+
|    spid               | player id of the HEOS | N/A                   |
|                       | device which is       |                       |
|                       | acting as the source  |                       |
+-----------------------+-----------------------+-----------------------+
|                       | Player id returned by |                       |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

+-----------------------+-----------------------+-----------------------+
|    input              | input source name     | "inputs/aux_in_1"     |
|                       |                       |                       |
|                       | Note: Validity of     | "inputs/aux_in_2"     |
|                       | Inputs depends on the | "inputs/aux_in_3"     |
|                       | type of source HEOS   | "inputs/aux_in_4"     |
|                       | device                | "inputs/line_in_1"    |
|                       |                       | "inputs/line_in_2"    |
|                       |                       | "inputs/line_in_3"    |
|                       |                       | "inputs/line_in_4"    |
|                       |                       | "inputs/coax_in_1"    |
|                       |                       | "inputs/coax_in_2"    |
|                       |                       | "inputs/coax_in_3"    |
|                       |                       | "inputs/coax_in_4"    |
|                       |                       | "inputs/optical_in_1" |
|                       |                       | "inputs/optical_in_2" |
|                       |                       | "inputs/optical_in_3" |
|                       |                       | "inputs/optical_in_4" |
|                       |                       | "inputs/hdmi_in_1"    |
|                       |                       | "inputs/hdmi_in_2"    |
|                       |                       | "inputs/hdmi_arc_1"   |
|                       |                       | "inputs/hdmi_arc_2"   |
+-----------------------+-----------------------+-----------------------+

..

   Response for command
   "heos://browse/play_input?pid=player_id&input=input_name" :

   **Note**: this command will cause a Now Playing Change Event to occur
   if an aux in stream is played.

   {

"heos": {

}

   }

   "command": "browse/play_input", "result": "success",

   "message": "pid=player_id&input=input_name"

   Examples: heos://browse/play_input?pid=1234&input=inputs/aux_in_1

   `heos://browse/play_input?pid=1234&spid=9876&input=i <heos://browse/play_input?pid=1234&amp;spid=9876&amp;input=i>`__\ nputs/aux_in_1
   heos://browse/play_stream?pid=1&sid=1441320818&mid=\ `i <heos://browse/play_input?pid=1234&amp;spid=9876&amp;input=i>`__\ nputs/aux_in_1

Add Container to Queue with Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://browse/add_to_queue?pid=player_id&sid=source_id&cid=container_id&aid=add_criteria

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | N/A                   |
|                       | by 'browse' or        |                       |
|                       | 'search' command      |                       |
+-----------------------+-----------------------+-----------------------+
|    aid                | Add criteria id as    | 1 – play now          |
|                       | defined by            |                       |
|                       | enumerations ->       |                       |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 2 – play next         |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 3 – add to end        |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 4 – replace and play  |
+-----------------------+-----------------------+-----------------------+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Note: The cid for this command must be a 'playable' container type.
   Response:

   **Note**: this command will cause a Now Playing Change Event to occur
   if a new song is played.

   {

"heos": {

}

   }

   "command": " browse/add_to_queue", "result": "success",

   "message":
   "pid='player_id'&sid='source_id'&cid='container_id'&aid='add_criteria'"

   Example: heos://browse/add_to_queue?pid=1&sid=5&cid=Artist/All&aid=2

   Supported Sources: Local Media Servers, Playlists, History, Rhapsody
   playable containers, Deezer playable containers, iHeartRadio playable

   containers, Napster playable containers

Add Track to Queue with Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://browse/add_to_queue?pid=player_id&sid=source_id&cid=container_id&mid=media_id&aid=add-criteria

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | N/A                   |
|                       | by 'browse' or        |                       |
|                       | 'search' command      |                       |
+-----------------------+-----------------------+-----------------------+
|    mid                | Media id returned by  | N/A                   |
|                       | 'browse' or 'search'  |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+
|    aid                | Add criteria id as    | 1 – play now          |
|                       | defined by            |                       |
|                       | enumerations ->       |                       |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 2 – play next         |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 3 – add to end        |
+-----------------------+-----------------------+-----------------------+
|                       |                       | 4 – replace and play  |
+-----------------------+-----------------------+-----------------------+
|    pid                | Player id returned by | N/A                   |
|                       | 'get_players' or      |                       |
|                       | 'get_groups' command  |                       |
+-----------------------+-----------------------+-----------------------+

..

   Note: The mid for this command must be a 'track' media type.
   Response:

   **Note**: this command will cause a Now Playing Change Event to occur
   if a new song is played.

   {

"heos": {

}

   }

   "command": " browse/add_to_queue", "result": "success",

   "message":
   "pid='player_id'&sid='source_id'&cid='container_id'&mid='media_id'&aid='add_criteria'"

   Example:
   heos://browse/add_to_queue?pid=1&sid=8&cid=Artists/All&mid=9&aid=1

   Supported Sources: Local Media Servers, Playlists, History, Rhapsody
   Tracks, Deezer Tracks, iHeartRadio Tracks, Napster

Get HEOS Playlists
~~~~~~~~~~~~~~~~~~

   Refer to Browse Sources and Browse Source Containers

Rename HEOS Playlist
~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://browse/rename_playlist?sid=source_id&cid=contaiiner_id&name=playlist_name

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command; select HEOS  |                       |
|                       | source to get HEOS    |                       |
|                       | playlists.            |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | N/A                   |
|                       | by 'browse' command;  |                       |
|                       | use Playlist          |                       |
|                       | container to get HEOS |                       |
|                       | playlists             |                       |
+-----------------------+-----------------------+-----------------------+
|    name               | String for new        | N/A                   |
|                       | playlist name limited |                       |
|                       | to 128 unicode        |                       |
|                       | characters            |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   {

"heos": {

}

   }

   "command": "browse/rename_playlist ", "result": "success",

   "message": "sid='source_id'&cid='contaiiner_id'&name='playlist_name'"

   Example: heos://browse/rename_playlist?sid=11&cid=234&name=new name

Delete HEOS Playlist
~~~~~~~~~~~~~~~~~~~~

   Command:
   heos://browse/delete_playlist?sid=source_id&cid=contaiiner_id

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Enumeration           |
+=======================+=======================+=======================+
|    sid                | Source id returned by | N/A                   |
|                       | 'get_music_sources'   |                       |
|                       | command; select HEOS  |                       |
|                       | source to get HEOS    |                       |
|                       | playlists.            |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | N/A                   |
|                       | by 'browse' command;  |                       |
|                       | use Playlist          |                       |
|                       | container to get HEOS |                       |
|                       | playlists             |                       |
+-----------------------+-----------------------+-----------------------+

..

   Response:

   **Note:** The HEOS History has two containers: one for songs and
   another for stations. The following response example is for the songs
   container. The station container returns the list of stations.

   {

"heos": {

}

   }

   "command": "browse/delete_playlist ", "result": "success",

   "message": "sid='source_id'&cid='contaiiner_id'

   Example: heos://browse/delete_playlist?sid=11&cid=234

Get HEOS History
~~~~~~~~~~~~~~~~

   Refer to Browse Sources and Browse Source Containers

Retrieve Album Metadata
~~~~~~~~~~~~~~~~~~~~~~~

   Retrieve image url associated with a given album id. This command
   facilitates controllers to retrieve and update their UI with cover
   art, if image_url in browse/search/get_queue/get_now_playing_media
   command response is blank.

   Command:
   `heos://browse/retrieve_metadata?sid=source_id&cid=album_id <heos://browse/add_to_queue?pid=player_id&amp;sid=source_id&amp;cid=container_id&amp;aid=add_criteria>`__

+-----------------------+-----------------------+-----------------------+
|    Attribute          | Description           | Comment               |
+=======================+=======================+=======================+
|    sid                | Source id returned by | Currently supported   |
|                       | 'get_music_sources'   | media sources are     |
|                       | command; select HEOS  | Rhapsody/Napster      |
|                       | source to get HEOS    |                       |
|                       | playlists.            |                       |
+-----------------------+-----------------------+-----------------------+
|    cid                | Container id returned | Rhapsody/Napster      |
|                       | by 'browse' command   | album ids             |
|                       | or                    |                       |
|                       | 'get_now_playing_medi |                       |
|                       | a'                    |                       |
|                       | command               |                       |
+-----------------------+-----------------------+-----------------------+

..

   Note: Supported music service is Rhapsody. Response:

   {

"heos": {

},

   "command": "browse/retrieve_metadata", "result": "success",

   "message":
   "sid=2&cid=album_id&returned=items_in_current_response&count=total_items_available"

   "payload": [

{

   "album_id": "album_id", "images": [

   {

   "image_url": "URL to image file", "width": current image width

   },

   .

   .

   .

   {

   "image_url": " URL to image file", "width": current image width

   }

   ]

   }

   ]

   }

   Example:
   `heos://browse/retrieve_metadata?sid=2&cid=Alb.184664171 <heos://browse/retrieve_metadata?sid=2&amp;cid=Alb.184664171>`__

Get Service Options for now playing screen - OBSOLETE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Obsolete - Now get_now_playing_media command will include supported
   option for currently playing media. Command:
   heos://browse/get_service_options?sid=source_id

   **Note**: This command returns service options that are only
   available on 'now playing' screen. Please refer to 'Browse Source'
   and 'Browse Source Containers' for service options available on
   various browse levels.

   **Note**: the following response provides examples of the various
   service options. The actual response will depend on the service
   options available for a given source type.

   Response:

   {

"heos": {

},

"payload": [

{

   "command": "browse/get_service_options", "result": "success",

   "message": ""

   "play": [

   {

   "id": 11,

   "name": "Thumbs Up"

   },

   {

   "id": 12,

   "name": "Thumbs Down"

   }

   ]

   }

   ]

   }

   Example: heos://browse/get_service_options?sid=5

Set service option
~~~~~~~~~~~~~~~~~~

   Set service option is a generic command used to select any of the
   supported service options provided through 'Get Service Options for
   now playing screen', 'Browse Sources' and 'Browse Source Containers'
   command response.

   Following service options are currently supported:

+-----------------------+-----------------------+-----------------------+
|    **Option id**      |    **Example          |    **Parameter        |
|                       |    Command**          |    description**      |
+=======================+=======================+=======================+
|    1 - Add Track to   |    heos://browse/set_ |    mid - track id     |
|    Library (Rhapsody) | service_option?sid=2& |    obtained through   |
|                       | option=1&\ **mid**\ = |    'browse source     |
|                       | Tra.1                 |    containers'        |
|                       |    74684187           |    command            |
+-----------------------+-----------------------+-----------------------+
|    2 - Add Album to   |    heos://browse/set_ |    cid - album id     |
|    Library            | service_option?sid=2& |    obtained through   |
|                       | option=2&\ **cid**\ = |    'browse source     |
|                       | Alb.17                |                       |
+-----------------------+-----------------------+-----------------------+
|    (Rhapsody)         |    4684186            |    containers'        |
|                       |                       |    command            |
+-----------------------+-----------------------+-----------------------+
|    3 - Add Station to |    heos://browse/set_ |    mid - station id   |
|    Library            | service_option?sid=2& |    obtained through   |
|                       | option=3&\ **mid**\ = |    'browse source     |
|                       | sas.6                 |                       |
+-----------------------+-----------------------+-----------------------+
|    (Rhapsody)         |    513639             |    containers'        |
|                       |                       |    command            |
+-----------------------+-----------------------+-----------------------+

+-----------------------+-----------------------+-----------------------+
|    4 - Add Playlist   |    heos://browse/set_ |    cid - playlist id  |
|    to Library         | service_option?sid=2& |    obtained through   |
|                       | option=4&\ **cid**\ = |    'browse source     |
|                       | LIBPL                 |                       |
+=======================+=======================+=======================+
|    (Rhapsody)         |    AYLIST-pp.17557314 |    containers'        |
|                       | 9&\ **name**\ =Lupe   |    command            |
|                       |    Fiasco             |                       |
+-----------------------+-----------------------+-----------------------+
|                       |                       |    name - name of the |
|                       |                       |    playlist obtained  |
|                       |                       |    through            |
+-----------------------+-----------------------+-----------------------+
|                       |                       |    'browse source     |
|                       |                       |    container' command |
+-----------------------+-----------------------+-----------------------+
|    5 - Remove Track   |    heos://browse/set_ |    mid - track id     |
|    from               | service_option?sid=2& |    obtained through   |
|                       | option=5&\ **mid**\ = |    'browse source     |
|                       | Tra.1                 |                       |
+-----------------------+-----------------------+-----------------------+
|    Library (Rhapsody) |    74684187           |    containers'        |
|                       |                       |    command            |
+-----------------------+-----------------------+-----------------------+
|    6 - Remove Album   |    heos://browse/set_ |    cid - album id     |
|    from               | service_option?sid=2& |    obtained through   |
|                       | option=6&\ **cid**\ = |    'browse source     |
|                       | LIBAL                 |                       |
+-----------------------+-----------------------+-----------------------+
|    Library (Rhapsody) |    BUM-Alb.174684186  |    containers'        |
|                       |                       |    command            |
+-----------------------+-----------------------+-----------------------+
|    7 - Remove Station |    heos://browse/set_ |    mid - station id   |
|    from               | service_option?sid=2& |    obtained through   |
|                       | option=7&\ **mid**\ = |    'browse source     |
|                       | sas.6                 |                       |
+-----------------------+-----------------------+-----------------------+
|    Library (Rhapsody) |    513639             |    containers'        |
|                       |                       |    command            |
+-----------------------+-----------------------+-----------------------+
|    8 - Remove         |    heos://browse/set_ |    cid - playlist id  |
|    Playlist from      | service_option?sid=2& |    obtained through   |
|                       | option=8&\ **cid**\ = |    'browse source     |
|                       | LIBPL                 |                       |
+-----------------------+-----------------------+-----------------------+
|    Library (Rhapsody) |    AYLIST-mp.18601772 |    containers'        |
|                       | 2                     |    command            |
+-----------------------+-----------------------+-----------------------+
|    11 - Thumbs Up     |    heos://browse/set_ |    pid - player id    |
|                       | service_option?sid=1& |    obtained through   |
|                       | option=11&\ **pid**\  |    'get_players'      |
|                       | =-4099                |                       |
+-----------------------+-----------------------+-----------------------+
|    (Pandora)          |    95282              |    command            |
+-----------------------+-----------------------+-----------------------+
|    12 - Thumbs Down   |    heos://browse/set_ |    pid - player id    |
|                       | service_option?sid=1& |    obtained through   |
|                       | option=12&\ **pid**\  |    'get_players'      |
|                       | =-4099                |                       |
+-----------------------+-----------------------+-----------------------+
|    (Pandora)          |    95282              |    command            |
+-----------------------+-----------------------+-----------------------+
|    13 - Create New    |    heos://browse/set_ |    name - search      |
|    Station (Pandora)  | service_option?sid=1& |    string for         |
|                       | option=13&\ **name**\ |    creating new       |
|                       |  =Lo                  |    station Note: This |
|                       |    ve                 |    command returns    |
|                       |                       |    station ids.       |
|                       |    `heos://browse/set |                       |
|                       | _service_option?sid=1 |    Controllers need   |
|                       | &option=13& <heos://b |    to                 |
|                       | rowse/set_service_opt |                       |
|                       | ion?sid=1&amp;option= |    use 'play station' |
|                       | 13>`__\ **name**\ =Lo |    command to play a  |
|                       |    ve&range=0, 10     |    station.           |
+-----------------------+-----------------------+-----------------------+
|    19 - Add station   |    heos://browse/set_ |    pid - player id    |
|    to HEOS Favorites  | service_option?option |    obtained through   |
|                       | =19&pid=-409995282    |    'get_players'      |
|                       |                       |    command            |
|                       |                       |                       |
|                       |                       |    Note: Adds         |
|                       |                       |    currently playing  |
|                       |                       |    station to HEOS    |
|                       |                       |    Favorites          |
+-----------------------+-----------------------+-----------------------+
|    20 - Remove from   |    heos://browse/set_ |    mid - station id   |
|    HEOS Favorites     | service_option?option |    obtained through   |
|                       | =20&mid=sas.651363    |    'browse source'    |
|                       |    9                  |    command on         |
|                       |                       |    Favorites          |
+-----------------------+-----------------------+-----------------------+

..

   Note: Option 13 (Create New Station) supports optional range queries.

   Response:

   {

"heos": {

}

   }

   "command": " browse/set_service_option", "result": "success",

   "message": "sid=source_id&option=option_id&mid=media_id"

   Example:
   heos://browse/set_service_option?sid=2&option=1&mid=Tra.174684187

5. .. rubric:: Change Events (Unsolicited Responses)
      :name: change-events-unsolicited-responses

   5. .. rubric:: Sources Changed
         :name: sources-changed

..

   Response:

   {

"heos": {

}

   }

   "command": "event/sources_changed",

Players Changed
---------------

   Response:

   {

"heos": {

}

   }

   "command": "event/players_changed",

Group Changed
-------------

   Response:

   {

"heos": {

}

   }

   "command": "event/groups_changed",

Source Data Changed
-------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/source_data_changed", "message": "sid='source_id'"

Player State Changed
--------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/player_state_changed", "message":
   "pid='player_id'&state='play_state'"

Player Now Playing Changed
--------------------------

   Response:

   {

"heos": {

}

   }

   "command": " event/player_now_playing_changed", "message":
   "pid='player_id'"

Player Now Playing Progress
---------------------------

   Response:

   {

"heos": {

}

   }

   "command": " event/player_now_playing_progress",

   "message": "pid=player_id&cur_pos=position_ms&duration=duration_ms"

Player Playback Error
---------------------

   Response:

   {

"heos": {

}

   }

   "command": " event/player_playback_error", "message":
   "pid=player_id&error=Could Not Download"

   Note: error string represents error type. Controller can directly
   display the error string to the user.

Player Queue Changed
--------------------

   Response:

   {

"heos": {

}

   }

   "command": " event/player_queue_changed", "message":
   "pid='player_id'"

Player Volume Changed
---------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/player_volume_changed ", "message":
   "pid='player_id'&level='vol_level'"

Player Mute Changed
-------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/player_mute_changed", "message":
   "pid='player_id'&state='on_or_off'"

Player Repeat Mode Changed
--------------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/repeat_mode_changed",

   "message": "pid=’player_id’&repeat='on_all_or_on_one_or_off'”

Player Shuffle Mode Changed
---------------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/shuffle_mode_changed", "message":
   "pid=’player_id’&shuffle='on_or_off'”

Group Status Changed
--------------------

   Response

   {

"heos": {

}

   }

   "command": "event/group_changed", "message": "gid='group_id'"

Group Volume Changed
--------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/group_volume_changed ", "message":
   "gid='group_id'&level='vol_level'"

Group Mute Changed
------------------

   Response:

   {

"heos": {

}

   }

   "command": "event/group_mute_changed", "message":
   "gid='group_id'&state='on_or_off'"

User Changed
------------

   Response:

   {

"heos": {

}

   }

   "command": "event/user_changed",

   "message": "signed_out" or "signed_in&un=<current user name>"

0. .. rubric:: Error Codes
      :name: error-codes

1. .. rubric:: General Error Response
      :name: general-error-response

..

   Respone:

   {

"heos": {

}

   }

   "command": "'command_group'/'command'", "result": "'fail'",

   "message": "eid="error_id&text=error text& *command_arguments'*"

Error Code and Text Table
-------------------------

+--------------------+-------------+------------------+
|    **Description** |    **Code** | **Text Example** |
+--------------------+-------------+------------------+

+-----------------------+-----------------------+-----------------------+
|    Unrecognized       |    1                  | Command not           |
|    Command            |                       | recognized.           |
+=======================+=======================+=======================+
|    Invalid ID         |    2                  | ID not valid          |
+-----------------------+-----------------------+-----------------------+
|    Wroing Number of   |    3                  | Command arguments not |
|    Command Arguments  |                       | correct.              |
+-----------------------+-----------------------+-----------------------+
|    Requested data not |    4                  | Requested data not    |
|    available          |                       | available.            |
+-----------------------+-----------------------+-----------------------+
|    Resource currently |    5                  | Resource currently    |
|    not available      |                       | not available.        |
+-----------------------+-----------------------+-----------------------+
|    Invalid            |    6                  | Invalid Credentials.  |
|    Credentials        |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    Command Could Not  |    7                  | Command not executed. |
|    Be Executed        |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    User not logged In |    8                  | User not logged in.   |
+-----------------------+-----------------------+-----------------------+
|    Parameter out of   |    9                  | Out of range          |
|    range              |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    User not found     |    10                 | User not found        |
+-----------------------+-----------------------+-----------------------+
|    Internal Error     |    11                 | System Internal Error |
+-----------------------+-----------------------+-----------------------+
|    System Error       |    12                 | System                |
|                       |                       | error&syserrno=-2     |
+-----------------------+-----------------------+-----------------------+
|    Processing         |    13                 | Processing previous   |
|    Previous Command   |                       | command               |
+-----------------------+-----------------------+-----------------------+
|    Media can't be     |    14                 | cannot play           |
|    played             |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    Option no          |    15                 | Option not supported  |
|    supported          |                       |                       |
+-----------------------+-----------------------+-----------------------+
