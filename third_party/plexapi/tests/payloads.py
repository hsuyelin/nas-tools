ACCOUNT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<user email="testuser@email.com" id="12345" uuid="1234567890" mailing_list_status="active" thumb="https://plex.tv/users/1234567890abcdef/avatar?c=12345" username="testuser" title="testuser" cloudSyncDevice="" locale="" authenticationToken="faketoken" authToken="faketoken" scrobbleTypes="" restricted="0" home="1" guest="0" queueEmail="queue+1234567890@save.plex.tv" queueUid="" hasPassword="true" homeSize="2" maxHomeSize="15" secure="1" certificateVersion="2">
  <subscription active="1" status="Active" plan="lifetime">
    <feature id="companions_sonos"/>
  </subscription>
  <roles>
    <role id="plexpass"/>
  </roles>
  <entitlements all="1"/>
  <profile_settings default_audio_language="en" default_subtitle_language="en" auto_select_subtitle="1" auto_select_audio="1" default_subtitle_accessibility="0" default_subtitle_forced="0"/>
  <services/>
  <username>testuser</username>
  <email>testuser@email.com</email>
  <joined-at type="datetime">2000-01-01 12:348:56 UTC</joined-at>
  <authentication-token>faketoken</authentication-token>
</user>
"""

SONOS_RESOURCES = """<MediaContainer size="3">
  <Player title="Speaker 1" machineIdentifier="RINCON_12345678901234561:1234567891" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.11"/>
  <Player title="Speaker 2 + 1" machineIdentifier="RINCON_12345678901234562:1234567892" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.12"/>
  <Player title="Speaker 3" machineIdentifier="RINCON_12345678901234563:1234567893" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.13"/>
</MediaContainer>
"""

SERVER_RESOURCES = """<MediaContainer size="3">
<StatisticsResources timespan="6" at="1609708609" hostCpuUtilization="0.000" processCpuUtilization="0.207" hostMemoryUtilization="64.946" processMemoryUtilization="3.665"/>
<StatisticsResources timespan="6" at="1609708614" hostCpuUtilization="5.000" processCpuUtilization="0.713" hostMemoryUtilization="64.939" processMemoryUtilization="3.666"/>
<StatisticsResources timespan="6" at="1609708619" hostCpuUtilization="10.000" processCpuUtilization="4.415" hostMemoryUtilization="64.281" processMemoryUtilization="3.669"/>
</MediaContainer>
"""

SERVER_TRANSCODE_SESSIONS = """<MediaContainer size="1">
<TranscodeSession key="qucs2leop3yzm0sng4urq1o0" throttled="0" complete="0" progress="1.2999999523162842" size="73138224" speed="6.4000000953674316" duration="6654989" remaining="988" context="streaming" sourceVideoCodec="h264" sourceAudioCodec="dca" videoDecision="transcode" audioDecision="transcode" protocol="dash" container="mp4" videoCodec="h264" audioCodec="aac" audioChannels="2" transcodeHwRequested="1" transcodeHwDecoding="dxva2" transcodeHwDecodingTitle="Windows (DXVA2)" transcodeHwEncoding="qsv" transcodeHwEncodingTitle="Intel (QuickSync)" transcodeHwFullPipeline="0" timeStamp="1611533677.0316164" maxOffsetAvailable="84.000667334000667" minOffsetAvailable="0" height="720" width="1280" />
</MediaContainer>
"""

MYPLEX_INVITE = """<MediaContainer friendlyName="myPlex" identifier="com.plexapp.plugins.myplex" machineIdentifier="xxxxxxxxxx" size="1">
<Invite id="12345" createdAt="1635126033" friend="1" home="1" server="1" username="testuser" email="testuser@email.com" thumb="https://plex.tv/users/1234567890abcdef/avatar?c=12345" friendlyName="testuser">
<Server name="testserver" numLibraries="2"/>
</Invite>
</MediaContainer>
"""
