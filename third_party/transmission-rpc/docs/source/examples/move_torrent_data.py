from transmission_rpc import Client

client = Client()

t = client.get_torrent(0)

client.move_torrent_data(t.hashString, location="/home/trim21/downloads/completed/")
