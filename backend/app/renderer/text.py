import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .. import config

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [config.FONT_PATH] if config.FONT_PATH else []
    candidates += _FONT_CANDIDATES
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class TextScroller:
    """텍스트를 매트릭스 폭보다 넓은 이미지로 한 번 렌더링해 두고
    가로로 스크롤하며 프레임을 만든다. speed는 px/s, 0이면 정지(가운데 정렬)."""

    def __init__(
        self,
        width: int,
        height: int,
        text: str,
        color: str = "#ffffff",
        bg: str = "#000000",
        speed: float = 40.0,
        font_size: int = 0,
    ):
        self.width = width
        self.height = height
        self.speed = speed
        font = _load_font(font_size or int(height * 0.7))

        measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        left, top, right, bottom = measure.textbbox((0, 0), text, font=font)
        text_w, text_h = right - left, bottom - top

        # 스크롤 시 텍스트가 화면 오른쪽 밖에서 들어와 왼쪽 밖으로 나가도록
        # 양옆에 매트릭스 폭만큼 여백을 둔다.
        pad = width if speed else max((width - text_w) // 2, 0)
        strip_w = text_w + pad * 2 if speed else max(width, text_w)
        strip = Image.new("RGB", (strip_w, height), bg)
        draw = ImageDraw.Draw(strip)
        draw.text((pad - left, (height - text_h) // 2 - top), text, font=font, fill=color)

        self._strip = np.asarray(strip, dtype=np.uint8)
        self._offset = 0.0
        self._loop_len = strip_w - width if strip_w > width else 0

    def next_frame(self, dt: float) -> np.ndarray:
        x = int(self._offset)
        frame = self._strip[:, x : x + self.width]
        if self.speed and self._loop_len:
            self._offset = (self._offset + self.speed * dt) % self._loop_len
        return np.ascontiguousarray(frame)
