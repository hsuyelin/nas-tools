:title:`General Settings`

**butlerUpdateChannel (text)**
  Update Channel. (default: 16; choices: 16:Public|8:Plex Pass)

**collectUsageData (bool)**
  Send anonymous usage data to Plex. This helps us improve your experience (for example, to help us match movies and TV shows). (default: True)

**friendlyName (text)**
  Friendly name. This name will be used to identify this media server to other computers on your network. If you leave it blank, your computer's name will be used instead.

**logDebug (bool)**
  Enable Plex Media Server debug logging. (default: True)

**logTokens (bool)**
  Allow Plex Media Server tokens in logs. Media server tokens can be used to gain access to library content. Don't share logs containing tokens publicly. A server restart is required for a change to take effect.

**logVerbose (bool)**
  Enable Plex Media Server verbose logging.


:title:`Scheduled Task Settings`

**butlerDatabaseBackupPath (text)**
  Backup directory. The directory in which database backups are stored. (default: /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases)

**butlerEndHour (int)**
  Time at which tasks stop running. The time at which the background maintenance tasks stop running. (default: 5; choices: 0:Midnight|1:1 am|2:2 am|3:3 am|4:4 am|5:5 am|6:6 am|7:7 am|8:8 am|9:9 am|10:10 am|11:11 am|12:Noon|13:1 pm|14:2 pm|15:3 pm|16:4 pm|17:5 pm|18:6 pm|19:7 pm|20:8 pm|21:9 pm|22:10 pm|23:11 pm)

**butlerStartHour (int)**
  Time at which tasks start to run. The time at which the server starts running background maintenance tasks. (default: 2; choices: 0:Midnight|1:1 am|2:2 am|3:3 am|4:4 am|5:5 am|6:6 am|7:7 am|8:8 am|9:9 am|10:10 am|11:11 am|12:Noon|13:1 pm|14:2 pm|15:3 pm|16:4 pm|17:5 pm|18:6 pm|19:7 pm|20:8 pm|21:9 pm|22:10 pm|23:11 pm)

**butlerTaskBackupDatabase (bool)**
  Backup database every three days. (default: True)

**butlerTaskCleanOldBundles (bool)**
  Remove old bundles every week. (default: True)

**butlerTaskCleanOldCacheFiles (bool)**
  Remove old cache files every week. (default: True)

**butlerTaskDeepMediaAnalysis (bool)**
  Perform extensive media analysis during maintenance. (default: True)

**butlerTaskGenerateAutoTags (bool)**
  Analyze and tag photos. (default: True)

**butlerTaskOptimizeDatabase (bool)**
  Optimize database every week. (default: True)

**butlerTaskRefreshEpgGuides (bool)**
  Perform refresh of program guide data.. (default: True)

**butlerTaskRefreshLibraries (bool)**
  Update all libraries during maintenance.

**butlerTaskRefreshLocalMedia (bool)**
  Refresh local metadata every three days. (default: True)

**butlerTaskRefreshPeriodicMetadata (bool)**
  Refresh metadata periodically. (default: True)

**butlerTaskUpgradeMediaAnalysis (bool)**
  Upgrade media analysis during maintenance. (default: True)


:title:`Channels Settings`

**disableCapabilityChecking (bool)**
  Disable capability checking. Capability checking ensures that plug-ins that are incompatible with this version of the server or the current client application you are using are hidden. Disabling capability checking is useful during development, but will enable access to plug-ins that may perform unreliably with certain client applications.

**iTunesLibraryXmlPath (text)**
  iTunes library XML path.

**iTunesSharingEnabled (bool)**
  Enable iTunes channel. A server restart is required for a change to take effect.

**pluginsLaunchTimeout (int)**
  Number of seconds to wait before a plugin times out. (default: 180)


:title:`DLNA Settings`

**dlnaAnnouncementLeaseTime (int)**
  DLNA server announcement lease time. Duration in seconds of DLNA Server SSDP announcement lease time. (default: 1800)

**dlnaClientPreferences (text)**
  DLNA client preferences. Client-specific configuration settings for the DLNA server.

**dlnaDefaultProtocolInfo (text)**
  DLNA default protocol info. Protocol info string used in GetProtocolInfo responses by the DLNA server. (default: http-get:*:video/mpeg:*,http-get:*:video/mp4:*,http-get:*:video/vnd.dlna.mpeg-tts:*,http-get:*:video/avi:*,http-get:*:video/x-matroska:*,http-get:*:video/x-ms-wmv:*,http-get:*:video/wtv:*,http-get:*:audio/mpeg:*,http-get:*:audio/mp3:*,http-get:*:audio/mp4:*,http-get:*:audio/x-ms-wma*,http-get:*:audio/wav:*,http-get:*:audio/L16:*,http-get:*image/jpeg:*,http-get:*image/png:*,http-get:*image/gif:*,http-get:*image/tiff:*)

**dlnaDescriptionIcons (text)**
  DLNA server description icons. Icons offered by DLNA server when devices request server description. (default: png,jpeg;260x260,120x120,48x48)

**dlnaDeviceDiscoveryInterval (int)**
  DLNA media renderer discovery interval. Number of seconds between DLNA media renderer discovery requests. (default: 60)

**dlnaEnabled (bool)**
  Enable the DLNA server. This allows the server to stream media to DLNA (Digital Living Network Alliance) devices. (default: True)

**dlnaPlatinumLoggingLevel (text)**
  DLNA server logging level. (default: OFF; choices: OFF|FATAL|SEVERE|WARNING|INFO|FINE|FINER|FINEST|ALL)

**dlnaReportTimeline (bool)**
  DLNA server timeline reporting. Enable the DLNA server to report timelines for video play activity. (default: True)


:title:`Extras Settings`

**cinemaTrailersFromBluRay (bool)**
  Include Cinema Trailers from new and upcoming movies on Blu-ray. This feature is Plex Pass only.

**cinemaTrailersFromLibrary (bool)**
  Include Cinema Trailers from movies in my library. (default: True)

**cinemaTrailersFromTheater (bool)**
  Include Cinema Trailers from new and upcoming movies in theaters. This feature is Plex Pass only.

**cinemaTrailersPrerollID (text)**
  Cinema Trailers pre-roll video. Copy and paste the video's detail page URL into this field.

**cinemaTrailersType (int)**
  Choose Cinema Trailers from. (default: 1; choices: 0:All movies|1:Only unwatched movies)


:title:`Library Settings`

**allowMediaDeletion (bool)**
  Allow media deletion. The owner of the server will be allowed to delete media files from disk. (default: True)

**autoEmptyTrash (bool)**
  Empty trash automatically after every scan. (default: True)

**fSEventLibraryPartialScanEnabled (bool)**
  Run a partial scan when changes are detected. When changes to library folders are detected, only scan the folder that changed.

**fSEventLibraryUpdatesEnabled (bool)**
  Update my library automatically. Your library will be updated automatically when changes to library folders are detected.

**generateBIFBehavior (text)**
  Generate video preview thumbnails. Video preview thumbnails provide live updates in Now Playing and while seeking on supported apps. Thumbnail generation may take a long time, cause high CPU usage, and consume additional disk space. You can turn off thumbnail generation for individual libraries in the library's advanced settings. (default: never; choices: never:never|scheduled:as a scheduled task|asap:as a scheduled task and when media is added)

**generateChapterThumbBehavior (text)**
  Generate chapter thumbnails. Chapter thumbnails provide images in the chapter view on supported apps. They can take a long time to generate and consume additional disk space. (default: scheduled; choices: never:never|scheduled:as a scheduled task|asap:as a scheduled task and when media is added)

**onDeckWindow (int)**
  Weeks to consider for On Deck. Shows that have not been watched in this many weeks will not appear in On Deck. (default: 16)

**scannerLowPriority (bool)**
  Run scanner tasks at a lower priority.

**scheduledLibraryUpdateInterval (int)**
  Library update interval. (default: 3600; choices: 900:every 15 minutes|1800:every 30 minutes|3600:hourly|7200:every 2 hours|21600:every 6 hours|43200:every 12 hours|86400:daily)

**scheduledLibraryUpdatesEnabled (bool)**
  Update my library periodically.

**watchMusicSections (bool)**
  Include music libraries in automatic updates. Linux systems limit the maximum number of watched directories; this may cause problems with large music libraries.


:title:`Network Settings`

**allowedNetworks (text)**
  List of IP addresses and networks that are allowed without auth. Comma separated list of IP addresses or IP/netmask entries for networks that are allowed to access Plex Media Server without logging in. When the server is signed out and this value is set, only localhost and addresses on this list will be allowed.

**configurationUrl (text)**
  Web Manager URL. (default: http://127.0.0.1:32400/web)

**customCertificateDomain (text)**
  Custom certificate domain. Domain name to be published to plex.tv using your mapped port; must match a name from the custom certificate file.

**customCertificateKey (text)**
  Custom certificate encryption key.

**customCertificatePath (text)**
  Custom certificate location. Path to a PKCS #12 file containing a certificate and private key to enable TLS support on a custom domain.

**customConnections (text)**
  Custom server access URLs. A comma-separated list of URLs (http or https) which are published up to plex.tv for server discovery.

**enableHttpPipelining (bool)**
  Enable HTTP Pipelining. This feature can enable higher performance in the HTTP server component. A server restart is required for a change to take effect. (default: True)

**enableIPv6 (bool)**
  Enable server support for IPv6.

**gdmEnabled (bool)**
  Enable local network discovery (GDM). This enables the media server to discover other servers and players on the local network. (default: True)

**lanNetworksBandwidth (text)**
  LAN Networks. Comma separated list of IP addresses or IP/netmask entries for networks that will be considered to be on the local network when enforcing bandwidth restrictions. If set, all other IP addresses will be considered to be on the external network and and will be subject to external network bandwidth restrictions. If left blank, only the server's subnet is considered to be on the local network.

**secureConnections (int)**
  Secure connections. When set to "Required", some unencrypted connections (originating from the Media Server computer) will still be allowed and apps that don't support secure connections will not be able to connect at all. (default: 1; choices: 0:Required|1:Preferred|2:Disabled)

**wanPerUserStreamCount (int)**
  Remote streams allowed per user. Maximum number of simultaneous streams each user is allowed when not on the local network. (choices: 0:Unlimited|1:1|2:2|3:3|4:4|5:5|6:6|7:7|8:8|9:9|10:10|11:11|12:12|13:13|14:14|15:15|16:16|17:17|18:18|19:19|20:20)

**webHooksEnabled (bool)**
  Webhooks. This feature enables your server to send events to external services. (default: True)


:title:`Transcoder Settings`

**hardwareAcceleratedCodecs (bool)**
  Use hardware acceleration when available (Experimental). Plex Media Server will attempt to use hardware-accelerated video codecs when encoding and decoding video. Hardware acceleration can make transcoding faster and allow more simultaneous video transcodes, but it can also reduce video quality and compatibility.

**segmentedTranscoderTimeout (int)**
  Segmented transcoder timeout. Timeout in seconds segmented transcodes wait for the transcoder to begin writing data. (default: 20)

**transcodeCountLimit (int)**
  Maximum simultaneous video transcode. Limit the number of simultaneous video transcode streams your server can utilize (choices: 0:Unlimited|1:1|2:2|3:3|4:4|5:5|6:6|7:7|8:8|9:9|10:10|11:11|12:12|13:13|14:14|15:15|16:16|17:17|18:18|19:19|20:20)

**transcoderDefaultDuration (int)**
  Transcoder default duration. Duration in minutes to use when transcoding something with an unknown duration. (default: 120)

**transcoderH264BackgroundPreset (text)**
  Background transcoding x264 preset. The x264 preset value used for background transcoding (Sync and Media Optimizer). Slower values will result in better video quality and smaller file sizes, but will take significantly longer to complete processing. (default: veryfast; choices: ultrafast:Ultra fast|superfast:Super fast|veryfast:Very fast|faster:Faster|fast:Fast|medium:Medium|slow:Slow|slower:Slower|veryslow:Very slow)

**transcoderPruneBuffer (int)**
  Transcoder default prune buffer. Amount in past seconds to retain before pruning segments from a transcode. (default: 300)

**transcoderQuality (int)**
  Transcoder quality. Quality profile used by the transcoder. (choices: 0:Automatic|1:Prefer higher speed encoding|2:Prefer higher quality encoding|3:Make my CPU hurt)

**transcoderTempDirectory (text)**
  Transcoder temporary directory. Directory to use when transcoding for temporary files.

**transcoderThrottleBuffer (int)**
  Transcoder default throttle buffer. Amount in seconds to buffer before throttling the transcoder. (default: 60)


:title:`Misc Settings`

**acceptedEULA (bool)**
  Has the user accepted the EULA.

**articleStrings (text)**
  Comma-separated list of strings considered articles when sorting titles. A server restart is required for a change to take effect.. (default: the,das,der,a,an,el,la)

**languageInCloud (bool)**
  Use language preferences from plex.tv.

**machineIdentifier (text)**
  A unique identifier for the machine.

**publishServerOnPlexOnlineKey (bool)**
  Publish server on Plex Online. Publishing a server makes it automatically available on your client devices without any configuration of your router.

**transcoderCanOnlyRemuxVideo (bool)**
  The transcoder can only remux video.

**transcoderVideoResolutionLimit (text)**
  Maximum video output resolution for the transcoder. (default: 0x0)

**wanPerStreamMaxUploadRate (int)**
  Limit remote stream bitrate. Set the maximum bitrate of a remote stream from this server. (choices: 0:Original (No limit)|20000:20 Mbps (1080p)|12000:12 Mbps (1080p)|10000:10 Mbps (1080p)|8000:8 Mbps (1080p)|4000:4 Mbps (720p)|3000:3 Mbps (720p)|2000:2 Mbps (480p)|1500:1.5 Mbps (480p)|720:720 kbps|320:320 kbps)

**wanTotalMaxUploadRate (int)**
  External network total upload limit (kbps). Speed at which to limit the total bandwidth not on the local network in kilobits per second. Use 0 to set no limit.


:title:`Undocumented Settings`

* **aBRKeepOldTranscodes (bool)**
* **allowHighOutputBitrates (bool)**
* **backgroundQueueIdlePaused (bool)**
* **butlerTaskGenerateMediaIndexFiles (bool)**
* **certificateVersion (int)**: default: 2
* **dvrShowUnsupportedDevices (bool)**
* **enableABRDebugOverlay (bool)**
* **enableAirplay (bool)**
* **eyeQUser (text)**
* **forceAutoAdjustQuality (bool)**
* **generateIndexFilesDuringAnalysis (bool)**
* **gracenoteUser (text)**
* **hardwareDevicePath (text)**: default: /dev/dri/renderD128
* **lastAutomaticMappedPort (int)**
* **manualPortMappingMode (bool)**
* **manualPortMappingPort (int)**: default: 32400
* **minimumProgressTime (int)**: default: 60000
* **plexMetricsUrl (text)**: default: https://metrics.plex.tv
* **plexOnlineMail (text)**
* **plexOnlineUrl (text)**: default: https://plex.tv
* **syncMyPlexLoginGCDeferral (int)**: default: 14400
* **syncPagingItemsLimit (int)**: default: 100
* **systemAudioCodecs (bool)**: default: True
* **transcoderH264MinimumCRF (double)**: default: 16.0
* **transcoderH264Options (text)**
* **transcoderH264OptionsOverride (text)**
* **transcoderH264Preset (text)**: default: veryfast
* **transcoderLivePruneBuffer (int)**: default: 5400
* **transcoderLogLevel (text)**: default: error

