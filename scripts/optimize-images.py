#!/usr/bin/env python3
"""Create resized, compressed homepage images and a 1200x630 social card."""

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


def circle_portrait(source: Image.Image, size: int) -> Image.Image:
    side = min(source.width, int(source.height * 0.78))
    left = (source.width - side) // 2
    top = int(source.height * 0.04)
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


def main() -> None:
    hero = Image.open(IMG / "hero-bg.jpg")
    profile = Image.open(IMG / "my-profile-img.jpg")
    hero_before = (IMG / "hero-bg.jpg").stat().st_size
    profile_before = (IMG / "my-profile-img.jpg").stat().st_size

    write_pair(hero, IMG / "hero-bg", 1600, jpeg_quality=78, webp_quality=74)
    write_pair(hero, IMG / "hero-bg-800", 800, jpeg_quality=78, webp_quality=74)
    write_pair(profile, IMG / "my-profile-img", 800, jpeg_quality=80, webp_quality=76)
    write_pair(profile, IMG / "my-profile-img-400", 400, jpeg_quality=80, webp_quality=76)

    card = social_card(profile)
    card_path = IMG / "og-card.jpg"
    save_jpeg(card, card_path, 86)

    skip = {
        IMG / "hero-bg.jpg",
        IMG / "hero-bg-800.jpg",
        IMG / "my-profile-img.jpg",
        IMG / "my-profile-img-400.jpg",
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


if __name__ == "__main__":
    main()
