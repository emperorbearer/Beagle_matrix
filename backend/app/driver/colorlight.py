import socket

import numpy as np

from .. import config
from .base import MatrixDriver

# Colorlight 5A-75B/E 프로토콜 — chubby75 리버스엔지니어링 문서 기반
# (https://github.com/q3k/chubby75). 카드는 MAC 주소를 검사하지 않으므로
# 목적지/출발지 MAC은 관례적으로 쓰이는 고정값을 사용한다.
# ⚠️ 바이트 배치는 펌웨어 버전에 따라 다를 수 있다 — 실물 카드에서
#    검증할 항목은 docs/hardware.md §5의 체크리스트 참고.
_DST_MAC = bytes.fromhex("112233445566")
_SRC_MAC = bytes.fromhex("222233445566")

# 이더넷 페이로드 1500바이트 제한: 행 헤더 7바이트 + 픽셀당 3바이트
_MAX_PIXELS_PER_PACKET = 497

_MIN_FRAME = 60  # FCS 제외 이더넷 최소 프레임 길이


def _pad(pkt: bytes) -> bytes:
    return pkt + b"\x00" * (_MIN_FRAME - len(pkt)) if len(pkt) < _MIN_FRAME else pkt


def build_row_packets(row: int, pixels: bytes) -> list[bytes]:
    """한 행(RGB888)을 0x55 타입 패킷들로 만든다. 타입 두 번째 바이트가
    행 번호 상위 바이트, 페이로드 첫 바이트가 하위 바이트."""
    packets = []
    total = len(pixels) // 3
    offset = 0
    while offset < total:
        count = min(_MAX_PIXELS_PER_PACKET, total - offset)
        pkt = (
            _DST_MAC + _SRC_MAC
            + bytes([0x55, (row >> 8) & 0xFF, row & 0xFF])
            + offset.to_bytes(2, "big")
            + count.to_bytes(2, "big")
            + b"\x08\x88"
            + pixels[offset * 3 : (offset + count) * 3]
        )
        packets.append(_pad(pkt))
        offset += count
    return packets


def build_display_packet(brightness: int) -> bytes:
    """0x0107 디스플레이(래치) 패킷 — 보낸 행들을 화면에 반영시킨다."""
    b = max(0, min(255, brightness))
    payload = bytearray(98)
    payload[21] = b
    payload[22] = 0x05
    payload[24] = b
    payload[25] = b
    payload[26] = b
    return _pad(_DST_MAC + _SRC_MAC + bytes([0x01, 0x07]) + bytes(payload))


class ColorlightDriver(MatrixDriver):
    """Colorlight 5A-75B/E 리시버 카드 드라이버.

    렌더링된 프레임을 raw 이더넷 패킷으로 카드에 보내면 HUB75 스캔은
    카드의 FPGA가 전담한다. AF_PACKET 소켓을 쓰므로 root(CAP_NET_RAW)로
    실행해야 하며, 카드는 COLORLIGHT_IFACE 인터페이스에 직결을 권장한다.
    """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self._sock: socket.socket | None = None
        self._brightness = int(255 * config.MATRIX_BRIGHTNESS / 100)

    def open(self) -> None:
        try:
            self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            self._sock.bind((config.COLORLIGHT_IFACE, 0))
        except PermissionError as e:
            raise RuntimeError(
                "raw 소켓을 열 수 없습니다 — colorlight 드라이버는 root"
                "(또는 CAP_NET_RAW)로 실행해야 합니다."
            ) from e
        except OSError as e:
            raise RuntimeError(
                f"인터페이스 {config.COLORLIGHT_IFACE!r}를 열 수 없습니다. "
                "COLORLIGHT_IFACE 환경변수를 확인하세요."
            ) from e

    def push(self, frame: np.ndarray) -> None:
        if self._sock is None:
            return
        for y in range(self.height):
            for pkt in build_row_packets(y, frame[y].tobytes()):
                self._sock.send(pkt)
        self._sock.send(build_display_packet(self._brightness))

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None
