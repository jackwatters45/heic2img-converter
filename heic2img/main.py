# heic2img.py
import argparse
from pathlib import Path
import sys
import subprocess
from tqdm import tqdm
import os
from typing import List, Dict, Any, Optional, Tuple

# Import Pillow and pillow-heif
try:
    import pillow_heif  # type: ignore
    from PIL import Image  # type: ignore

    dependencies_available = True
except ImportError:
    dependencies_available = False


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    global dependencies_available

    if dependencies_available:
        return True

    print("Required dependencies not found. Installing...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pillow", "pillow-heif"]
        )
        # Try importing again after installation
        global pillow_heif, Image
        import pillow_heif  # type: ignore
        from PIL import Image  # type: ignore

        dependencies_available = True
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def convert_heic(
    input_path: Path,
    output_path: Path,
    quality: int = 75,
    resize: Optional[Tuple[int, int]] = None,
    max_size: Optional[int] = None,
    max_file_size_mb: float = 2.0,
) -> bool:
    """Convert HEIC image to desired format using Pillow with aggressive compression.

    Args:
        input_path: Path to the HEIC file
        output_path: Path to save the converted file
        quality: Quality setting (0-100, lower = smaller file size)
        resize: Optional tuple of (width, height) to resize the image
        max_size: Optional maximum dimension (width or height)
        max_file_size_mb: Maximum file size in MB (default: 2.0)

    Returns:
        bool: True if conversion was successful, False otherwise
    """
    if not dependencies_available and not check_dependencies():
        return False

    try:
        # Register HEIF opener with Pillow
        pillow_heif.register_heif_opener()  # type: ignore

        # Open the HEIC image
        img = Image.open(str(input_path))  # type: ignore

        # Resize if requested
        if resize:
            img = img.resize(resize, Image.LANCZOS)  # type: ignore

        # Resize to max dimension if specified
        if max_size:
            width, height = img.size
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                img = img.resize((new_width, new_height), Image.LANCZOS)  # type: ignore

        # Set format-specific options with aggressive compression
        format_options: Dict[str, Any] = {}
        if output_path.suffix.lower() in [".jpg", ".jpeg"]:
            format_options = {"quality": quality, "optimize": True, "progressive": True}
        elif output_path.suffix.lower() == ".png":
            format_options = {
                "optimize": True,
                "compress_level": 9,
            }  # Maximum compression
        elif output_path.suffix.lower() == ".webp":
            format_options = {
                "quality": quality,
                "method": 6,
                "lossless": False,
            }  # method 6 = best compression

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as the target format with specified quality
        img.save(str(output_path), **format_options)  # type: ignore

        # Check if the file size exceeds the maximum and apply additional compression if needed
        max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # Try progressively lower quality settings until file size is under the limit
        current_quality = quality
        min_quality = 20  # Don't go below this quality to avoid extremely poor images

        while (
            os.path.getsize(output_path) > max_file_size_bytes
            and current_quality > min_quality
        ):
            # Reduce quality by 10 points each iteration
            current_quality -= 10

            # Only JPG and WebP support quality adjustment
            if output_path.suffix.lower() in [".jpg", ".jpeg"]:
                format_options["quality"] = current_quality
                img.save(str(output_path), **format_options)  # type: ignore
            elif output_path.suffix.lower() == ".webp":
                format_options["quality"] = current_quality
                img.save(str(output_path), **format_options)  # type: ignore
            else:
                # For PNG, we can't easily reduce quality further, so try reducing dimensions
                if max_size is None:
                    # If max_size wasn't specified, use current dimensions as starting point
                    current_width, current_height = img.size
                    max_size = max(current_width, current_height)
                else:
                    current_width, current_height = img.size

                # Reduce dimensions by 20% each iteration
                max_size = int(max_size * 0.8)

                if current_width > current_height:
                    new_width = max_size
                    new_height = int(current_height * (max_size / current_width))
                else:
                    new_height = max_size
                    new_width = int(current_width * (max_size / current_height))

                img = img.resize((new_width, new_height), Image.LANCZOS)  # type: ignore
                img.save(str(output_path), **format_options)  # type: ignore

        # If we still exceed the file size limit after all attempts, warn the user
        if os.path.getsize(output_path) > max_file_size_bytes:
            print(
                f"Warning: Could not reduce {output_path} below {max_file_size_mb}MB. Current size: {os.path.getsize(output_path) / (1024 * 1024):.2f}MB"
            )

        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert HEIC files to other formats with size optimization"
    )
    parser.add_argument("input_dir", help="Directory containing HEIC files")
    parser.add_argument("-o", "--output", help="Output directory (optional)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["jpg", "png", "webp"],
        default="jpg",
        help="Output format (default: jpg)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=75,
        help="Quality setting (0-100, lower = smaller file size, default: 75)",
    )
    parser.add_argument(
        "-m",
        "--max-size",
        type=int,
        help="Maximum dimension (width or height) in pixels",
    )
    parser.add_argument(
        "--max-file-size",
        type=float,
        default=2.0,
        help="Maximum file size in MB (default: 2.0)",
    )
    parser.add_argument(
        "-D",
        "--delete-originals",
        action="store_true",
        help="Delete original HEIC files and associated MP4 files after successful conversion",
    )
    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        print("Failed to install required dependencies. Please install manually:")
        print("pip install pillow pillow-heif")
        return 1

    # Setup paths
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output) if args.output else input_dir

    # Check if input directory exists
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return 1

    # Handle output directory creation
    if not output_dir.exists():
        response = input(
            f"Output directory '{output_dir}' does not exist. Create it? [y/N] "
        )
        if response.lower() != "y":
            print("Aborting...")
            return 1
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return 1

    # Find all HEIC files (case-insensitive)
    heic_files: List[Path] = [
        f
        for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in [".heic", ".heif"]
    ]

    if not heic_files:
        print("No HEIC files found in the specified directory!")
        return 1

    print(f"Found {len(heic_files)} HEIC files")

    # Track successful conversions for deletion
    successful_conversions: List[Path] = []
    # Track associated MP4 files for deletion if requested
    associated_mp4_files: List[Path] = []

    # Convert files
    for file in tqdm(heic_files, desc="Converting"):
        output_path = output_dir / f"{file.stem}.{args.format.lower()}"
        success = convert_heic(
            file,
            output_path,
            quality=args.quality,
            max_size=args.max_size,
            max_file_size_mb=args.max_file_size,
        )
        if success:
            successful_conversions.append(file)
            # Check for associated MP4 file
            mp4_file = input_dir / f"{file.stem}.mp4"
            if mp4_file.exists():
                associated_mp4_files.append(mp4_file)

    # Delete original files if requested
    if args.delete_originals and successful_conversions:
        delete_count = 0
        for file_path in successful_conversions:
            try:
                file_path.unlink()
                delete_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        # Delete associated MP4 files if requested
        mp4_delete_count = 0
        if associated_mp4_files:
            for mp4_file in associated_mp4_files:
                try:
                    mp4_file.unlink()
                    mp4_delete_count += 1
                except Exception as e:
                    print(f"Error deleting MP4 file {mp4_file}: {e}")

        print(
            f"Deleted {delete_count} original HEIC files and {mp4_delete_count} associated MP4 files"
        )

    print("Conversion complete!")
    return 0


if __name__ == "__main__":
    main()
