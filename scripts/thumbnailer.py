#!/usr/bin/env python3
"""Resize an image to a 16:9 thumbnail (1280x720 by default).

    python scripts/thumbnailer.py logo.png                 # writes logo-thumb.png
    python scripts/thumbnailer.py photo.jpg -o thumb.jpg
    python scripts/thumbnailer.py banner.png --fit pad     # keep the whole image
    python scripts/thumbnailer.py https://example.org/figure.png

  --fit crop  (default) fills the frame and trims the edges that don't fit.
              Good for photos, maps and plots.
  --fit pad   fits the whole image inside the frame and fills the rest with
              --background. Good for logos and banners with text near the edges.

The input can be a file or an http(s) URL. Needs Pillow (pip install Pillow);
it isn't in requirements.txt because the site build doesn't use it.
"""
import argparse
import io
import pathlib
import sys
import urllib.error
import urllib.request

try:
    from PIL import Image, ImageColor, ImageOps, UnidentifiedImageError
except ImportError:
    sys.exit("This script needs Pillow: pip install Pillow")

ASPECT = (16, 9)
MAX_DOWNLOAD = 50 * 1024 * 1024  # bytes


def load(source):
    """Open a local path or an http(s) URL as a Pillow image."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as resp:
            data = resp.read(MAX_DOWNLOAD + 1)
        if len(data) > MAX_DOWNLOAD:
            sys.exit(f"{source} is larger than {MAX_DOWNLOAD // 2**20} MB")
        image = Image.open(io.BytesIO(data))
    else:
        image = Image.open(source)
    # Apply any EXIF rotation so phone photos come out upright.
    return ImageOps.exif_transpose(image)


def default_output(source):
    name = pathlib.PurePosixPath(source.split("?", 1)[0]).name or "image.png"
    path = pathlib.Path(name)
    return path.with_name(f"{path.stem}-thumb{path.suffix or '.png'}")


def make_thumbnail(image, size, fit, background):
    if fit == "crop":
        return ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
    image = image.convert("RGBA" if has_alpha else "RGB")
    image = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
    canvas = Image.new(image.mode, size, ImageColor.getcolor(background, image.mode))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
                 image if has_alpha else None)
    return canvas


def output_format(path):
    fmt = Image.registered_extensions().get(path.suffix.lower())
    if fmt not in ("PNG", "JPEG", "WEBP"):
        sys.exit(f"Can't write {path}: use a .png, .jpg or .webp file name")
    return fmt


def save(image, path, fmt, quality):
    if fmt == "JPEG" and image.mode != "RGB":
        # JPEG has no transparency: flatten onto white.
        rgba = image.convert("RGBA")
        flat = Image.new("RGB", rgba.size, "white")
        flat.paste(rgba, mask=rgba.getchannel("A"))
        image = flat
    options = {"PNG": {"optimize": True},
               "JPEG": {"quality": quality, "optimize": True, "progressive": True},
               "WEBP": {"quality": quality, "method": 6}}.get(fmt, {})
    image.save(path, fmt, **options)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="image file or http(s) URL")
    parser.add_argument("-o", "--output", type=pathlib.Path,
                        help="output file; the extension sets the format "
                             "(default: <name>-thumb.<ext> in the current folder)")
    parser.add_argument("--width", type=int, default=1280,
                        help="output width in pixels; height is 9/16 of it (default 1280)")
    parser.add_argument("--fit", choices=["crop", "pad"], default="crop",
                        help="crop to fill the frame, or pad to keep the whole image (default crop)")
    parser.add_argument("--background", default="white",
                        help="padding colour for --fit pad, e.g. white, #0d1117 (default white)")
    parser.add_argument("--quality", type=int, default=85,
                        help="JPEG/WebP quality, 1-95 (default 85)")
    args = parser.parse_args()

    size = (args.width, round(args.width * ASPECT[1] / ASPECT[0]))
    try:
        ImageColor.getrgb(args.background)
    except ValueError:
        sys.exit(f"Not a colour: {args.background}")

    output = args.output or default_output(args.source)
    fmt = output_format(output)

    try:
        image = load(args.source)
    except FileNotFoundError:
        sys.exit(f"No such file: {args.source}")
    except UnidentifiedImageError:
        sys.exit(f"Not an image Pillow can read: {args.source}")
    except (urllib.error.URLError, TimeoutError) as err:
        sys.exit(f"Couldn't download {args.source}: {err}")
    if image.width < size[0] and image.height < size[1]:
        print(f"Note: the source is only {image.width}x{image.height}, "
              f"so it will be scaled up and may look soft.", file=sys.stderr)

    save(make_thumbnail(image, size, args.fit, args.background), output, fmt, args.quality)
    print(f"Wrote {output} ({size[0]}x{size[1]}, {output.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
