import time
from peer_table import PeerTable

table = PeerTable(suspect_after=2, dead_after=4)

print(table.update("Node-1", "127.0.0.1", 5001))

time.sleep(2.5)
print("Changes:", table.sweep())

time.sleep(2)
print("Changes:", table.sweep())

print("Final peers:", table.peers)