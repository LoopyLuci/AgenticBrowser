import socket

import pytest


def test_udp_discovery_beacon_responds_to_discover():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)

    try:
        sock.sendto(b"DISCOVER", ("<broadcast>", 43789))
        data, _ = sock.recvfrom(1024)
        payload = data.decode("utf-8")
        assert "agenticbrowser-control" in payload or "controlPort" in payload
    finally:
        sock.close()
