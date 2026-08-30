"""
Unit tests for cross-platform network connection scanning in LiveSystemMonitor.
"""
from __future__ import annotations

import socket
import sys
from collections import namedtuple
from unittest.mock import MagicMock, patch

from ulpf.collectors.live_monitor import LiveSystemMonitor

Addr = namedtuple("Addr", ["ip", "port"])
MockSConn = namedtuple("MockSConn", ["fd", "family", "type", "laddr", "raddr", "status", "pid"])


def test_scan_network_connections_posix_mock():
    monitor = LiveSystemMonitor(interval_ms=1000)
    monitor.is_windows = False
    monitor.os_type = "Linux"

    mock_connections = [
        # Active HTTPS outbound connection
        MockSConn(
            fd=3,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            laddr=Addr(ip="192.168.1.100", port=54321),
            raddr=Addr(ip="104.16.123.96", port=443),
            status="ESTABLISHED",
            pid=1234,
        ),
        # Active MySQL connection to local database
        MockSConn(
            fd=4,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            laddr=Addr(ip="127.0.0.1", port=43210),
            raddr=Addr(ip="127.0.0.1", port=3306),
            status="ESTABLISHED",
            pid=5678,
        ),
        # Listening socket (no raddr) -> should be skipped
        MockSConn(
            fd=5,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            laddr=Addr(ip="0.0.0.0", port=8000),
            raddr=None,
            status="LISTEN",
            pid=9999,
        ),
    ]

    mock_psutil = MagicMock()
    mock_psutil.net_connections.return_value = mock_connections

    with patch.dict(sys.modules, {"psutil": mock_psutil}):
        conns = monitor._scan_network_connections_posix()
        assert len(conns) == 2

        c1 = conns[0]
        assert c1["pid"] == 1234
        assert c1["src_ip"] == "192.168.1.100"
        assert c1["src_port"] == 54321
        assert c1["dst_ip"] == "104.16.123.96"
        assert c1["dst_port"] == 443
        assert c1["proto"] == "tcp"
        assert c1["state"] == "ESTABLISHED"
        assert c1["service_inferred"] == "HTTPS Web"
        assert c1["is_localhost"] is False

        c2 = conns[1]
        assert c2["pid"] == 5678
        assert c2["src_ip"] == "127.0.0.1"
        assert c2["dst_ip"] == "127.0.0.1"
        assert c2["dst_port"] == 3306
        assert c2["service_inferred"] == "MySQL Database"
        assert c2["is_localhost"] is True


def test_get_active_connections_posix():
    monitor = LiveSystemMonitor(interval_ms=1000)
    monitor.is_windows = False
    monitor.known_pids = {
        1234: {"name": "curl", "path": "/usr/bin/curl"},
    }

    mock_connections = [
        MockSConn(
            fd=3,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            laddr=Addr(ip="10.0.0.5", port=50000),
            raddr=Addr(ip="1.1.1.1", port=443),
            status="ESTABLISHED",
            pid=1234,
        ),
    ]

    mock_psutil = MagicMock()
    mock_psutil.net_connections.return_value = mock_connections

    with patch.dict(sys.modules, {"psutil": mock_psutil}):
        resolved = monitor.get_active_connections()
        assert len(resolved) == 1
        assert resolved[0]["pid"] == 1234
        assert resolved[0]["process_name"] == "curl"
        assert resolved[0]["process_path"] == "/usr/bin/curl"
        assert resolved[0]["dst_ip"] == "1.1.1.1"
        assert resolved[0]["dst_port"] == 443
