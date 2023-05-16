from transmission_rpc import Client

client = Client()

t = client.get_torrent(0)

client.change_torrent(
    t.hashString,
    files_unwanted=[f.id for f in t.get_files() if f.name.endswith(".txt")],
    priority_high=[f.id for f in t.get_files() if f.name.endswith(".mp4")],
    priority_low=[f.id for f in t.get_files() if f.name.endswith(".txt")],
)
