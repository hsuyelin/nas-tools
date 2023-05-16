Configuration
=============
Python-PlexAPI will work fine without any configuration. However, sometimes there are things you
may wish to alter for more control of the default behavior. The default configuration file path
is :samp:`~/.config/plexapi/config.ini` which can be overridden by setting the environment variable
:samp:`PLEXAPI_CONFIG_PATH` with the file path you desire. All configuration variables in this file
are optional. An example config.ini file may look like the following with all possible value specified. 

.. code-block:: ini

    # ~/.config/plexapi/config.ini
    [plexapi]
    container_size = 50
    timeout = 30

    [auth]
    myplex_username = johndoe
    myplex_password = kodi-stinks
    server_baseurl = http://127.0.0.1:32400
    server_token = XBHSMSJSDJ763JSm
    client_baseurl = http://127.0.0.1:32433
    client_token = BDFSLCNSNL789FH7

    [header]
    identifier = 0x485b314307f3L
    platorm = Linux
    platform_version = 4.4.0-62-generic
    product = PlexAPI
    version = 3.0.0

    [log]
    backup_count = 3
    format = %(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s
    level = INFO
    path = ~/.config/plexapi/plexapi.log
    rotate_bytes = 512000
    show_secrets = false
    

Environment Variables
---------------------
All configuration values can be set or overridden via environment variables. The environment variable
names are in all upper case and  follow the format :samp:`PLEXAPI_<SECTION>_<NAME>`. For example, if
you wish to set the log path via an environment variable, you may specify: `PLEXAPI_LOG_PATH="/tmp/plexapi.log"`


Section [plexapi] Options
-------------------------
**container_size**
    Default max results to return in on single search page. Looping through result pages is done
    internally by the API. Therefore, tuning this setting will not affect usage of plexapi. However,
    it help improve performance for large media collections (default: 50).

**timeout**
    Timeout in seconds to use when making requests to the Plex Media Server or Plex Client
    resources (default: 30).

**enable_fast_connect**
    By default Plex will be trying to connect with all available connection methods simultaneously,
    combining local and remote addresses, http and https, and be waiting for all connection to
    establish (or fail due to timeout / any other error), this can take long time when you're trying
    to connect to your Plex Server outside of your home network.

    When the options is set to `true` the connection procedure will be aborted with first successfully
    established connection.


Section [auth] Options
----------------------
**myplex_username**
    Default MyPlex (plex.tv) username to use when creating a new :any:`MyPlexAccount` object. Specifying
    this along with :samp:`auth.myplex_password` allow you to more easily connect to your account and
    remove the need to hard code the username and password in any supplemental scripts you may write. To
    create an account object using these values you may simply specify :samp:`account = MyPlexAccount()`
    without any arguments (default: None).

**myplex_password**
    Default MyPlex (plex.tv) password to use when creating a new :any:`MyPlexAccount` object. See
    `auth.myplex_password` for more information and example usage (default: None).

    WARNING: When specifying a password or token in the configuration file, be sure lock it down
    (permission 600) to ensure no other users on the system can read them. Or better yet, only specify
    sensitive values as a local environment variables.

**server_baseurl**
    Default baseurl to use when creating a new :any:`PlexServer` object. Specifying this along with
    :samp:`auth.server_token` allow you to more easily connect to a server and remove the need to hard
    code the baseurl and token in any supplemental scripts you may write. To create a server object using
    these values you may simply specify :samp:`plex = PlexServer()` without any arguments (default: None).

**server_token**
    Default token to use when creating a new :any:`PlexServer` object. See `auth.server_baseurl` for more
    information and example usage (default: None).

    WARNING: When specifying a password or token in the configuration file, be sure lock it down
    (permission 600) to ensure no other users on the system can read them. Or better yet, only specify
    sensitive values as a local environment variables.

**client_baseurl**
    Default baseurl to use when creating a new :any:`PlexClient` object. Specifying this along with
    :samp:`auth.client_token` allow you to more easily connect to a client and remove the need to hard
    code the baseurl and token in any supplemental scripts you may write. To create a client object using
    these values you may simply specify :samp:`client = PlexClient()` without any arguments (default: None).

**client_token**
    Default token to use when creating a new :any:`PlexClient` object. See `auth.client_baseurl` for more
    information and example usage (default: None).

    WARNING: When specifying a password or token in the configuration file, be sure lock it down
    (permission 600) to ensure no other users on the system can read them. Or better yet, only specify
    sensitive values as a local environment variables.


Section [header] Options
------------------------
**device**
    Header value used for X_PLEX_DEVICE to all Plex server and Plex client requests. Example devices
    include: iPhone, FireTV, Linux (default: `result of platform.uname()[0]`).

**device_name**
    Header value used for X_PLEX_DEVICE_NAME to all Plex server and Plex client requests. Example device
    names include: hostname or phone name (default: `result of platform.uname()[1]`).

**identifier**
    Header value used for X_PLEX_IDENTIFIER to all Plex server and Plex client requests. This is generally
    a UUID, serial number, or other number unique id for the device (default: `result of hex(uuid.getnode())`).

**platform**
    Header value used for X_PLEX_PLATFORM to all Plex server and Plex client requests. Example platforms
    include: iOS, MacOSX, Android, LG (default: `result of platform.uname()[0]`).

**platform_version**
    Header value used for X_PLEX_PLATFORM_VERSION to all Plex server and Plex client requests. This is
    generally the server or client operating system version: 4.3.1, 10.6.7, 3.2 (default: `result of
    platform.uname()[2]`).

**product**
    Header value used for X_PLEX_PRODUCT to all Plex server and Plex client requests. This is the Plex
    application name: Laika, Plex Media Server, Media Link (default: PlexAPI).

**provides**
    Header value used for X_PLEX_PROVIDES to all Plex server and Plex client requests This is generally one
    or more of: controller, player, server (default: PlexAPI).

**version**
    Header value used for X_PLEX_VERSION to all Plex server and Plex client requests. This is the Plex
    application version (default: plexapi.VERSION).


Section [log] Options
---------------------
**backup_count**
    Number backup log files to keep before rotating out old logs (default 3).

**format**
    Log file format to use for plexapi logging. (default:
    '%(asctime)s %(module)12s:%(lineno)-4s %(levelname)-9s %(message)s').
    Ref: https://docs.python.org/2/library/logging.html#logrecord-attributes

**level**
    Log level to use when for plexapi logging (default: INFO).

**path**
    File path to save plexapi logs to. If not specified, plexapi will not save logs to an output
    file (default: None).

**rotate_bytes**
    Max size of the log file before rotating logs to a backup file (default: 512000 equals 0.5MB).

**show_secrets**
    By default Plex will hide all passwords and token values when logging. Set this to 'true' to enable
    logging these secrets. This should only be done on a private server and only enabled when needed
    (default: false).
