from transmission_rpc import Client

client = Client()

client.change_torrent(
    0,
    upload_limited=True,  # don't forget this
    upload_limit=100,
    download_limited=True,
    download_limit=100,
)
