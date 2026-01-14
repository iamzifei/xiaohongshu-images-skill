#!/usr/bin/env python3
"""
Screenshot Capture Script for Xiaohongshu Images

Captures sequential screenshots of an HTML page at 3:4 aspect ratio,
ensuring no text is cut off at boundaries.

Usage:
    python screenshot.py <html_file_path>

Output:
    Screenshots saved to <html_folder>/screenshots/01.png, 02.png, etc.
"""

import os
import sys
import json
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)


# Screenshot dimensions for Xiaohongshu 3:4 ratio
SCREENSHOT_WIDTH = 1080
SCREENSHOT_HEIGHT = 1440  # 3:4 ratio


def find_safe_cut_point(page, y_position: int, search_range: int = 100) -> int:
    """
    Find a safe cutting point near y_position where no text is cut.

    Searches upward from y_position to find a gap between text elements.

    Args:
        page: Playwright page object
        y_position: Target Y position to cut
        search_range: How far to search upward for safe point

    Returns:
        Safe Y position to cut at
    """
    # JavaScript to find text boundaries near the cut point
    script = f"""
    () => {{
        const targetY = {y_position};
        const searchRange = {search_range};

        // Get all text-containing elements
        const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, span, a, code, pre, blockquote');

        let safeCutPoint = targetY;
        let minGap = Infinity;

        // Find elements that might be cut
        for (const el of textElements) {{
            const rect = el.getBoundingClientRect();
            const elTop = rect.top + window.scrollY;
            const elBottom = rect.bottom + window.scrollY;

            // Check if this element would be cut at targetY
            if (elTop < targetY && elBottom > targetY) {{
                // This element would be cut, find gap above it
                const gapAbove = targetY - elTop;
                if (gapAbove < searchRange && gapAbove < minGap) {{
                    // Cut above this element instead
                    safeCutPoint = Math.max(0, elTop - 10);
                    minGap = gapAbove;
                }}
            }}
        }}

        // Also check for line breaks within text blocks
        // Find the nearest paragraph boundary
        const paragraphs = document.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6');
        for (const p of paragraphs) {{
            const rect = p.getBoundingClientRect();
            const pBottom = rect.bottom + window.scrollY;

            // If paragraph ends near our cut point, prefer cutting there
            if (pBottom < targetY && targetY - pBottom < searchRange) {{
                const gap = targetY - pBottom;
                if (gap < minGap) {{
                    safeCutPoint = pBottom + 5;
                    minGap = gap;
                }}
            }}
        }}

        return Math.max(0, Math.floor(safeCutPoint));
    }}
    """

    try:
        safe_y = page.evaluate(script)
        return safe_y if safe_y > 0 else y_position
    except Exception as e:
        print(f"  Warning: Could not find safe cut point: {e}")
        return y_position


def capture_screenshots(html_path: Path, output_dir: Path):
    """
    Capture sequential screenshots of an HTML page.

    Args:
        html_path: Path to the HTML file
        output_dir: Directory to save screenshots
    """
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print(f"Opening: {html_path}")
    print(f"Screenshots will be saved to: {screenshots_dir}")
    print(f"Screenshot size: {SCREENSHOT_WIDTH}x{SCREENSHOT_HEIGHT} (3:4 ratio)")
    print()

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)

        # Create page with specific viewport
        context = browser.new_context(
            viewport={"width": SCREENSHOT_WIDTH, "height": SCREENSHOT_HEIGHT},
            device_scale_factor=2  # Retina quality
        )
        page = context.new_page()

        # Navigate to the HTML file
        file_url = f"file://{html_path.resolve()}"
        page.goto(file_url, wait_until="networkidle")

        # Wait for fonts and images to load
        page.wait_for_timeout(2000)

        # Get total page height
        total_height = page.evaluate("() => document.documentElement.scrollHeight")
        print(f"Total page height: {total_height}px")

        # Calculate number of screenshots needed
        current_y = 0
        screenshot_index = 1
        captured_screenshots = []

        while current_y < total_height:
            # Calculate the target end position for this screenshot
            target_end_y = current_y + SCREENSHOT_HEIGHT

            if target_end_y >= total_height:
                # Last screenshot - capture whatever remains
                actual_height = total_height - current_y

                # Scroll to position
                page.evaluate(f"window.scrollTo(0, {current_y})")
                page.wait_for_timeout(200)

                # Take screenshot
                filename = f"{screenshot_index:02d}.png"
                filepath = screenshots_dir / filename

                # For the last screenshot, we might have less than full height
                # Add white padding if needed
                page.screenshot(
                    path=str(filepath),
                    clip={
                        "x": 0,
                        "y": 0,
                        "width": SCREENSHOT_WIDTH,
                        "height": min(SCREENSHOT_HEIGHT, actual_height + 50)  # Small buffer
                    }
                )

                print(f"  Captured: {filename} (final, {actual_height}px of content)")
                captured_screenshots.append(str(filepath))
                break
            else:
                # Find safe cut point to avoid cutting text
                safe_end_y = find_safe_cut_point(page, target_end_y)
                actual_height = safe_end_y - current_y

                # Ensure we make progress even if safe cut point is the same
                if actual_height < SCREENSHOT_HEIGHT * 0.5:
                    actual_height = SCREENSHOT_HEIGHT
                    safe_end_y = current_y + actual_height

                # Scroll to position
                page.evaluate(f"window.scrollTo(0, {current_y})")
                page.wait_for_timeout(200)

                # Take screenshot
                filename = f"{screenshot_index:02d}.png"
                filepath = screenshots_dir / filename

                page.screenshot(
                    path=str(filepath),
                    clip={
                        "x": 0,
                        "y": 0,
                        "width": SCREENSHOT_WIDTH,
                        "height": SCREENSHOT_HEIGHT
                    }
                )

                print(f"  Captured: {filename} (y: {current_y} to {safe_end_y})")
                captured_screenshots.append(str(filepath))

                # Move to next section
                current_y = safe_end_y
                screenshot_index += 1

        browser.close()

    return captured_screenshots


def main():
    if len(sys.argv) < 2:
        print("Usage: python screenshot.py <html_file_path>")
        print()
        print("Captures sequential 3:4 ratio screenshots of an HTML page.")
        print("Screenshots are saved to <html_folder>/screenshots/")
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()

    if not html_path.exists():
        print(f"Error: File does not exist: {html_path}")
        sys.exit(1)

    if not html_path.suffix.lower() in ['.html', '.htm']:
        print(f"Warning: File does not appear to be HTML: {html_path}")

    # Output directory is the same as HTML file's directory
    output_dir = html_path.parent

    print("=" * 60)
    print("Xiaohongshu Screenshot Capture")
    print("=" * 60)

    try:
        screenshots = capture_screenshots(html_path, output_dir)

        print()
        print("=" * 60)
        print(f"Screenshot capture complete!")
        print(f"Total screenshots: {len(screenshots)}")
        print(f"Location: {output_dir / 'screenshots'}")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"Error during screenshot capture: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
