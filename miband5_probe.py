"""Phase 0 BLE capture for an already-bound Mi Smart Band 5.

Huami UUID and challenge-response adapted from Erencv/miband5-ble (MIT).
See LICENSE-Erencv.txt and the source links in BAO-CAO.md.
"""

import argparse
import asyncio
import csv
import getpass
import logging
import math
import re
import struct
import sys
import time
import warnings
from contextlib import AsyncExitStack, ExitStack
from datetime import UTC, datetime
from pathlib import Path

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
from Crypto.Cipher import AES


def huami(code):
    return f"0000{code}-0000-3512-2118-0009af100700"


def standard(code):
    return f"0000{code}-0000-1000-8000-00805f9b34fb"


AUTH = huami("0009")
CONTROL = huami("0001")
DATA = huami("0002")
HR_CONTROL = standard("2a39")
HR_DATA = standard("2a37")
START = (b"\x01\x03\x19", b"\x01\x03\x00\x00\x00\x19", b"\x02")
HR_STOP = (b"\x15\x01\x00", b"\x15\x02\x00")
MARKERS = {
    "0": "other", "1": "brake", "2": "gas", "3": "brake_to_gas",
    "4": "gas_to_brake", "s": "sync",
}
LOG = logging.getLogger("miband5_phase0")


def local_key():
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        value = getpass.getpass("Existing Mi Band 5 auth key (hidden): ").strip()
    if value.lower().startswith("0x"):
        value = value[2:]
    if not re.fullmatch(r"[0-9a-fA-F]{32}", value):
        raise ValueError("Expected exactly 32 hex characters")
    return bytes.fromhex(value)


async def logged_cleanup(label, operation, *args, **kwargs):
    try:
        await asyncio.wait_for(operation(*args, **kwargs), 5)
    except (BleakError, OSError, RuntimeError, TimeoutError) as exc:
        LOG.warning("cleanup_failed operation=%s error_type=%s", label, type(exc).__name__)


def require_char(client, service_uuid, uuid, *properties):
    service = client.services.get_service(service_uuid)
    char = service.get_characteristic(uuid) if service else None
    if char is None or not set(properties) <= set(char.properties):
        raise RuntimeError(f"Missing GATT endpoint/properties: {uuid} {properties}")
    return char


async def subscribe(client, cleanup, char, callback):
    # Register before setup in case the backend fails after changing the CCCD.
    cleanup.push_async_callback(
        logged_cleanup, char.uuid, client.stop_notify, char
    )
    await asyncio.wait_for(client.start_notify(char, callback), 10)


async def authenticate(client, char, key):
    replies = asyncio.Queue()

    def on_auth(_sender, data):
        if len(data) >= 3 and data[0] == 0x10:
            replies.put_nowait(bytes(data))

    async def reply(command):
        async with asyncio.timeout(12):
            while True:
                data = await replies.get()
                if data[1] == command:
                    return data

    async with AsyncExitStack() as cleanup:
        await subscribe(client, cleanup, char, on_auth)
        await asyncio.wait_for(client.write_gatt_char(char, b"\x02\x00", response=False), 8)
        challenge = await reply(0x02)
        if challenge[2] not in (0x01, 0x81) or len(challenge) != 19:
            raise RuntimeError(f"Auth challenge rejected/invalid, status=0x{challenge[2]:02x}")
        encrypted = AES.new(key, AES.MODE_ECB).encrypt(challenge[3:])
        await asyncio.wait_for(
            client.write_gatt_char(char, b"\x03\x00" + encrypted, response=False), 8
        )
        result = await reply(0x03)
        if result[2] != 0x01:
            raise RuntimeError(f"Auth response rejected, status=0x{result[2]:02x}")
    LOG.info("auth_ok")


async def inventory(client):
    for service in client.services:
        LOG.info("gatt_service=%s", service.uuid)
        for char in service.characteristics:
            LOG.info("gatt_char=%s properties=%s", char.uuid, ",".join(char.properties))
    info = client.services.get_service(standard("180a"))
    for code, label in (("2a27", "hardware"), ("2a26", "firmware"), ("2a28", "software")):
        char = info.get_characteristic(standard(code)) if info else None
        if char is None or "read" not in char.properties:
            LOG.info("%s=unavailable", label)
            continue
        try:
            data = await asyncio.wait_for(client.read_gatt_char(char), 5)
        except (BleakError, OSError, TimeoutError):
            LOG.info("%s=read_failed", label)
        else:
            LOG.info("%s=%r", label, bytes(data).decode("ascii", "replace").strip("\0"))


def csv_output(stack, directory, filename, fields):
    stream = stack.enter_context((directory / filename).open("x", encoding="utf-8", newline=""))
    writer = csv.writer(stream)
    writer.writerow(fields)
    return stream, writer


class Capture:
    def __init__(self, stack, directory):
        self.origin_ns = time.monotonic_ns()
        LOG.info("origin_utc=%s origin_monotonic_ns=%d", datetime.now(UTC).isoformat(), self.origin_ns)
        self.raw_file, self.raw = csv_output(
            stack, directory, "packets.csv",
            ("rx_ns", "packet_id", "channel", "length", "payload_hex", "decode_status", "sample_count"),
        )
        self.samples_file, self.samples = csv_output(
            stack, directory, "samples.csv",
            ("rx_ns", "packet_id", "sample_in_packet", "x_raw", "y_raw", "z_raw"),
        )
        self.events_file, self.events = csv_output(
            stack, directory, "markers.csv", ("rx_ns", "event"),
        )
        self.packet_id = 0
        self.data_batches = []
        self.decode_error = None

    def now(self):
        return time.monotonic_ns() - self.origin_ns

    def mark(self, event):
        when = self.now()
        self.events.writerow((when, event))
        self.events_file.flush()
        LOG.info("event=%s rx_ns=%d", event, when)
        return when

    def packet(self, sender, payload):
        when = self.now()
        self.packet_id += 1
        data = bytes(payload)
        channel = "data" if sender.uuid == DATA else "control"
        status, count = "control", 0
        if channel == "data":
            if not data or data[0] != 0:
                status = "unknown_type"
            elif len(data) < 8 or (len(data) - 2) % 6:
                status = "invalid_length"
            else:
                status = "type00_xyz_candidate"
                for index, xyz in enumerate(struct.iter_unpack("<hhh", data[2:])):
                    self.samples.writerow((when, self.packet_id, index, *xyz))
                    count += 1
            self.data_batches.append((when, count))
        self.raw.writerow((when, self.packet_id, channel, len(data), data.hex(), status, count))

    def summary(self, start, end):
        data = [(when, count) for when, count in self.data_batches if start <= when < end]
        decoded = [(when, count) for when, count in data if count]
        seconds = (end - start) / 1e9
        LOG.info(
            "capture_s=%.3f data_notifications=%d candidate_batches=%d candidate_samples=%d",
            seconds, len(data), len(decoded), sum(count for _, count in decoded),
        )
        if seconds <= 0:
            return False
        # Includes the edges of the capture window for maximum-gap assessment.
        edges = [start, *(when for when, _ in decoded), end]
        gaps = sorted((b - a) / 1e6 for a, b in zip(edges, edges[1:]))
        LOG.info(
            "notifications_per_s=%.2f candidate_samples_per_s=%.2f "
            "candidate_batch_gap_p95_ms=%.1f candidate_batch_gap_max_ms=%.1f",
            len(data) / seconds, sum(count for _, count in decoded) / seconds,
            gaps[math.ceil(0.95 * len(gaps)) - 1], gaps[-1],
        )
        for offset_s in range(5, (end - start) // 1_000_000_000 - 9, 10):
            left = start + offset_s * 1_000_000_000
            right = left + 10_000_000_000
            window_samples = sum(count for when, count in decoded if left <= when < right)
            LOG.info("window_start_s=%d window_s=10 candidate_samples_per_s=%.2f",
                     offset_s, window_samples / 10)
        return bool(decoded)

    def flush(self):
        self.raw_file.flush()
        self.samples_file.flush()


async def read_commands(capture, client, raw, hr, disconnected, seconds):
    import msvcrt

    LOG.info("Keys: 1 brake, 2 gas, 3 brake_to_gas, 4 gas_to_brake, 0 other, s sync, q stop")
    start = capture.mark("capture_start")
    next_ping = start + 10_000_000_000
    next_flush = start + 1_000_000_000
    ticks = 0
    try:
        while capture.now() - start < seconds * 1e9 and not disconnected.is_set():
            if capture.decode_error:
                raise capture.decode_error
            if msvcrt.kbhit():
                key = msvcrt.getwch()
                if key in ("\x00", "\xe0"):
                    msvcrt.getwch()
                elif key.lower() == "q":
                    break
                elif key.lower() in MARKERS:
                    capture.mark(MARKERS[key.lower()])
            now = capture.now()
            if now >= next_flush:
                capture.flush()
                next_flush = now + 1_000_000_000
            if hr is not None and now >= next_ping:
                next_ping += 10_000_000_000
                ticks += 1
                await write_live(client, hr, b"\x16", response=True)
                if ticks % 5 == 0:
                    await write_live(client, raw, b"\x00", response=False)
            await asyncio.sleep(0.02)
    finally:
        end = capture.mark("capture_end")
        found = capture.summary(start, end)
    if disconnected.is_set():
        raise RuntimeError("BLE disconnected during capture")
    return found


async def write_live(client, char, payload, *, response):
    LOG.info("stream_write char=%s cmd=%s", char.uuid, payload.hex())
    await asyncio.wait_for(client.write_gatt_char(char, payload, response=response), 8)


async def stop_live(client, char, payload, *, response):
    await logged_cleanup(payload.hex(), write_live, client, char, payload, response=response)


async def stream(client, args, capture, disconnected):
    auth = require_char(client, standard("fee1"), AUTH, "notify", "write-without-response")
    raw = require_char(client, standard("fee0"), CONTROL, "notify", "write-without-response")
    data = require_char(client, standard("fee0"), DATA, "notify")
    hr = hr_data = None
    if args.profile == "flutter":
        hr = require_char(client, standard("180d"), HR_CONTROL, "write")
        hr_data = require_char(client, standard("180d"), HR_DATA, "notify")

    key = local_key()
    await authenticate(client, auth, key)
    del key

    def on_packet(sender, payload):
        if capture.decode_error is None:
            try:
                capture.packet(sender, payload)
            except (OSError, csv.Error, ValueError) as exc:
                capture.decode_error = exc

    async with AsyncExitStack() as cleanup:
        if hr is not None:
            await subscribe(client, cleanup, hr_data, lambda _sender, _data: None)
        await subscribe(client, cleanup, raw, on_packet)
        await subscribe(client, cleanup, data, on_packet)
        if hr is not None:
            for command in reversed(HR_STOP):
                cleanup.push_async_callback(stop_live, client, hr, command, response=True)
            for command in (b"\x15\x02\x00", b"\x15\x01\x00", b"\x15\x01\x01"):
                await write_live(client, hr, command, response=True)
        cleanup.push_async_callback(stop_live, client, raw, b"\x03", response=False)
        for command in START:
            await write_live(client, raw, command, response=False)
        return await read_commands(capture, client, raw, hr, disconnected, args.seconds)


async def run(args):
    if args.mode == "scan":
        devices = await BleakScanner.discover(timeout=12, return_adv=True)
        for device, advertisement in devices.values():
            name = advertisement.local_name or device.name
            if name and "band" in name.lower():
                print(f"{device.address}  {name}  RSSI={advertisement.rssi}")
        return 0

    if sys.platform != "win32":
        raise RuntimeError("Use a Windows PC with BLE for this command")
    if args.mode == "capture" and (not sys.stdin.isatty() or not sys.stderr.isatty()):
        raise RuntimeError("Capture requires an interactive Windows console")

    directory = args.out / datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    directory.mkdir(parents=True, exist_ok=False)
    with ExitStack() as stack:
        handler = logging.FileHandler(directory / "run.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        LOG.addHandler(handler)
        stack.callback(handler.close)
        stack.callback(LOG.removeHandler, handler)
        LOG.info("mode=%s profile=%s windows=%s output=%s", args.mode,
                 getattr(args, "profile", "none"), sys.getwindowsversion().build, directory.name)
        try:
            device = await BleakScanner.find_device_by_address(args.address, timeout=20)
            if device is None:
                raise RuntimeError("Target not found. Wake the band and pause phone Bluetooth")
            disconnected = asyncio.Event()
            async with BleakClient(
                device, timeout=20, pair=False,
                disconnected_callback=lambda _client: disconnected.set(),
            ) as client:
                await inventory(client)
                if args.mode == "inspect":
                    LOG.info("files=%s result=gatt_inventory", directory)
                    return 0
                capture = Capture(stack, directory)
                found = await stream(client, args, capture, disconnected)
            LOG.info("files=%s result=%s", directory, "candidate_data" if found else "no_candidate_data")
            return 0 if found else 2
        except (BleakError, OSError, RuntimeError, ValueError, TimeoutError, getpass.GetPassWarning) as exc:
            # Do not copy backend exception text into the log (it can contain device identifiers).
            LOG.error("capture_failed error_type=%s", type(exc).__name__)
            raise
        except asyncio.CancelledError:
            LOG.info("capture_interrupted")
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    modes.add_parser("scan", help="List nearby devices whose advertised name contains 'band'")
    inspect = modes.add_parser("inspect", help="Record GATT topology and version reads")
    inspect.add_argument("--address", required=True, help="Exact address from scan")
    inspect.add_argument("--out", type=Path, default=Path("runs"))
    capture = modes.add_parser("capture", help="Collect stream on an already-bound band")
    capture.add_argument("--address", required=True, help="Exact address from scan")
    capture.add_argument("--profile", choices=("raw", "flutter"), default="raw")
    capture.add_argument("--seconds", type=int, default=60)
    capture.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()
    if args.mode == "capture" and not 1 <= args.seconds <= 1800:
        parser.error("--seconds must be between 1 and 1800")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    LOG.setLevel(logging.INFO)
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        return 130
    except getpass.GetPassWarning:
        LOG.error("Hidden key entry is unavailable. Use an interactive Windows terminal")
        return 1
    except (BleakError, OSError, RuntimeError, ValueError, TimeoutError, EOFError) as exc:
        LOG.error("%s: %s", type(exc).__name__, exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
