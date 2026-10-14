#!/usr/bin/env python3
"""Create resized, compressed homepage images and a 1200x630 social card.

The public portrait is a face-centered 4:5 crop of the full original. The
sidebar avatar and about photo both use object-fit: cover, which previously
framed the forest around the subject instead of his face.
"""

import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "img"


def save_jpeg(image: Image.Image, path: Path, quality: int) -> None:
    image.convert("RGB").save(
        path,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
    )


def save_webp(image: Image.Image, path: Path, quality: int) -> None:
    image.convert("RGB").save(path, format="WEBP", quality=quality, method=6)


def resize_width(image: Image.Image, width: int) -> Image.Image:
    image = image.convert("RGB")
    if image.width == width:
        return image
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def write_pair(image: Image.Image, stem: Path, width: int, jpeg_quality: int, webp_quality: int) -> None:
    resized = resize_width(image, width)
    save_jpeg(resized, stem.with_suffix(".jpg"), jpeg_quality)
    save_webp(resized, stem.with_suffix(".webp"), webp_quality)


def recompress_oversized(path: Path, max_edge: int = 1600, quality: int = 78) -> None:
    before = path.stat().st_size
    if before < 100 * 1024:
        return
    image = Image.open(path).convert("RGB")
    edge = max(image.size)
    if edge > max_edge:
        scale = max_edge / edge
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            Image.Resampling.LANCZOS,
        )
    save_jpeg(image, path, quality)
    after = path.stat().st_size
    print(f"recompress {path.relative_to(ROOT)}: {before/1024:.1f}KB -> {after/1024:.1f}KB {image.size}")


# OpenCV YuNet detection on the original 800x1062 portrait (score 0.95).
# Used when the detector or its model is unavailable.
FALLBACK_FACE = (363, 329, 103, 137)
YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
ORIGINAL_PORTRAIT = IMG / "my-profile-img-original.jpg"


def yunet_model() -> Path | None:
    cached = Path("/tmp/face_detection_yunet_2023mar.onnx")
    if cached.exists() and cached.stat().st_size > 100_000:
        return cached
    try:
        urllib.request.urlretrieve(YUNET_URL, cached)
    except OSError:
        return None
    return cached if cached.exists() else None


def detect_face(image: Image.Image) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the primary face in source pixels."""
    width, height = image.size
    try:
        import cv2
        import numpy as np
    except ImportError:
        return FALLBACK_FACE
    model = yunet_model()
    if model is None or not hasattr(cv2, "FaceDetectorYN"):
        return FALLBACK_FACE
    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.FaceDetectorYN.create(str(model), "", (width, height), 0.6, 0.3, 5000)
    _, faces = detector.detect(bgr)
    if faces is None or len(faces) == 0:
        return FALLBACK_FACE
    best = max(faces, key=lambda face: float(face[-1]))
    x, y, w, h = [int(round(value)) for value in best[:4]]
    if w < 40 or h < 40 or x < 0 or y < 0 or x + w > width or y + h > height:
        return FALLBACK_FACE
    return (x, y, w, h)


def face_centered_portrait(source: Image.Image) -> Image.Image:
    """4:5 crop with the eyes near 42% of the height and a little headroom.

    Width is about four face-widths, which keeps the shoulders and a margin of
    background without letting the environment take over the frame.
    """
    x, y, w, h = detect_face(source)
    eyes_y = y + 0.38 * h
    center_x = x + w / 2
    crop_w = int(round(w * 3.9))
    crop_h = int(round(crop_w * 5 / 4))
    crop_w = min(crop_w, source.width)
    crop_h = min(crop_h, source.height)
    left = int(round(center_x - crop_w / 2))
    top = int(round(eyes_y - 0.42 * crop_h))
    left = max(0, min(left, source.width - crop_w))
    top = max(0, min(top, source.height - crop_h))
    return source.crop((left, top, left + crop_w, top + crop_h))


def ensure_original_portrait() -> Image.Image:
    """Keep the full environmental portrait so the face crop can be regenerated."""
    display = IMG / "my-profile-img.jpg"
    if not ORIGINAL_PORTRAIT.exists():
        ORIGINAL_PORTRAIT.write_bytes(display.read_bytes())
    return Image.open(ORIGINAL_PORTRAIT).convert("RGB")


def circle_portrait(source: Image.Image, size: int) -> Image.Image:
    """Circular avatar from a face-centered portrait, keeping the hair inside the circle."""
    side = min(source.width, source.height)
    left = max(0, (source.width - side) // 2)
    # Anchor to the top of the portrait. The crop already places the eyes near
    # 42% and leaves headroom above the hair; starting lower would clip that hair
    # against the circular mask.
    top = 0
    if source.height > side:
        top = max(0, min(source.height - side, int(round(source.height * 0.42 - side * 0.50))))
    crop = source.crop((left, top, left + side, top + side)).resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(crop, (0, 0))
    result.putalpha(mask)
    return result


def social_card(portrait: Image.Image) -> Image.Image:
    width, height = 1200, 630
    card = Image.new("RGB", (width, height), "#040b14")
    draw = ImageDraw.Draw(card)
    draw.rectangle((0, 0, 16, height), fill="#149ddd")

    regular = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Regular.ttf", 28)
    medium = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Medium.ttf", 36)
    bold = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Bold.ttf", 72)
    small = ImageFont.truetype("/usr/share/fonts/truetype/macos/Inter-Regular.ttf", 24)

    avatar = circle_portrait(portrait, 360)
    ring = Image.new("RGBA", (392, 392), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, 391, 391), outline="#149ddd", width=8)
    ax, ay = 92, 119
    card.paste(avatar, (ax + 16, ay + 16), avatar)
    card.paste(ring, (ax, ay), ring)

    text_x = 540
    draw.text((text_x, 168), "Pikesh Maharjan", font=bold, fill="#ffffff")
    draw.text((text_x, 268), "Data Engineer", font=medium, fill="#149ddd")
    draw.text((text_x, 340), "ETL, data quality, Azure and Databricks", font=regular, fill="#d5dde6")
    draw.text((text_x, 470), "pikeshmaharjan.com.np", font=small, fill="#a8a9b4")
    return card


def write_profile(portrait: Image.Image) -> None:
    """Write the face crop at its native size, plus a 400px-wide variant."""
    save_jpeg(portrait, IMG / "my-profile-img.jpg", 84)
    save_webp(portrait, IMG / "my-profile-img.webp", 80)
    write_pair(portrait, IMG / "my-profile-img-400", min(400, portrait.width), jpeg_quality=84, webp_quality=80)


def main() -> None:
    hero = Image.open(IMG / "hero-bg.jpg")
    hero_before = (IMG / "hero-bg.jpg").stat().st_size
    profile_before = (IMG / "my-profile-img.jpg").stat().st_size

    write_pair(hero, IMG / "hero-bg", 1600, jpeg_quality=78, webp_quality=74)
    write_pair(hero, IMG / "hero-bg-800", 800, jpeg_quality=78, webp_quality=74)
    portrait = face_centered_portrait(ensure_original_portrait())
    write_profile(portrait)

    card = social_card(portrait)
    card_path = IMG / "og-card.jpg"
    save_jpeg(card, card_path, 86)

    skip = {
        IMG / "hero-bg.jpg",
        IMG / "hero-bg-800.jpg",
        IMG / "my-profile-img.jpg",
        IMG / "my-profile-img-400.jpg",
        ORIGINAL_PORTRAIT,
        card_path,
    }
    for path in IMG.rglob("*.jpg"):
        if path in skip:
            continue
        recompress_oversized(path)

    print("--- homepage candidates ---")
    for path in [
        IMG / "hero-bg.jpg",
        IMG / "hero-bg.webp",
        IMG / "hero-bg-800.jpg",
        IMG / "hero-bg-800.webp",
        IMG / "my-profile-img.jpg",
        IMG / "my-profile-img.webp",
        IMG / "my-profile-img-400.jpg",
        IMG / "my-profile-img-400.webp",
        card_path,
    ]:
        with Image.open(path) as image:
            print(f"{path.stat().st_size/1024:8.1f}KB {image.size[0]}x{image.size[1]} {path.name}")
    hero_after = (IMG / "hero-bg.webp").stat().st_size
    profile_after = (IMG / "my-profile-img.webp").stat().st_size
    saved = (hero_before + profile_before) - (hero_after + profile_after)
    print(f"hero+portrait webp savings vs originals: {saved/1024/1024:.2f}MB")


def refresh_portrait() -> None:
    """Regenerate the face-centered portrait and the social card only."""
    source = ensure_original_portrait()
    print("face", detect_face(source))
    portrait = face_centered_portrait(source)
    write_profile(portrait)
    card_path = IMG / "og-card.jpg"
    save_jpeg(social_card(portrait), card_path, 86)
    for path in (
        IMG / "my-profile-img.jpg",
        IMG / "my-profile-img.webp",
        IMG / "my-profile-img-400.jpg",
        IMG / "my-profile-img-400.webp",
        card_path,
        ORIGINAL_PORTRAIT,
    ):
        with Image.open(path) as image:
            print(f"{path.stat().st_size/1024:8.1f}KB {image.size[0]}x{image.size[1]} {path.name}")


if __name__ == "__main__":
    import sys

    if "--portrait" in sys.argv:
        refresh_portrait()
    else:
        main()
