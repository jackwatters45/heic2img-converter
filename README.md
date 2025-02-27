# HEIC2IMG Converter

A simple command-line tool to convert HEIC/HEIF images (commonly used by iPhones) to more widely compatible formats like JPG, PNG, or WebP with aggressive file size optimization.

## Features

- Convert HEIC/HEIF images to JPG, PNG, or WebP formats
- Aggressive file size optimization for sharing on platforms like Facebook Marketplace or Craigslist
- Automatic file size limiting (default 2MB maximum)
- Resize images to reduce file size even further
- Option to delete original HEIC files and associated MP4 files after conversion
- Batch processing of multiple files
- Simple command-line interface

## Installation

```bash
pip install heic2img-converter
```

## Usage

Basic usage:

```bash
heic2img /path/to/heic/files
```

This will convert all HEIC files in the specified directory to JPG format with default compression settings.

### Options

```bash
heic2img [input_dir] [options]

options:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory (optional)
  -f {jpg,png,webp}, --format {jpg,png,webp}
                        Output format (default: jpg)
  -q QUALITY, --quality QUALITY
                        Quality setting (0-100, lower = smaller file size, default: 75)
  -m MAX_SIZE, --max-size MAX_SIZE
                        Maximum dimension (width or height) in pixels
  --max-file-size MAX_FILE_SIZE
                        Maximum file size in MB (default: 2.0)
  --delete-originals    Delete original HEIC files and associated MP4 files after successful conversion
```

### Examples

Convert all HEIC files to JPG with maximum compression (smallest file size):

```bash
heic2img /path/to/heic/files -q 50
```

Convert to WebP format (often provides better compression than JPG):

```bash
heic2img /path/to/heic/files -f webp -q 60
```

Resize images to a maximum of 1200 pixels (width or height) while converting:

```bash
heic2img /path/to/heic/files -m 1200
```

Set a custom maximum file size (e.g., 1MB):

```bash
heic2img /path/to/heic/files --max-file-size 1.0
```

Convert to a different directory:

```bash
heic2img /path/to/heic/files -o /path/to/output
```

Convert and delete original HEIC files and associated MP4 files:

```bash
heic2img /path/to/heic/files --delete-originals
```

## Tips for Smallest File Size

For platforms like Facebook Marketplace or Craigslist where image quality isn't critical:

1. Use WebP format for best compression: `-f webp`
2. Lower the quality setting: `-q 50` (or even lower if acceptable)
3. Resize large images: `-m 1200` (or smaller if acceptable)
4. Set a strict file size limit: `--max-file-size 1.0` (for 1MB maximum)

Example for maximum compression:

```bash
heic2img /path/to/heic/files -f webp -q 40 -m 1000 --max-file-size 1.0
```

## Requirements

- Python 3.11+
- Pillow
- pillow-heif
- tqdm

## Roadmap

- [ ] AI naming for output folders

## License

MIT
