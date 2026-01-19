# Xiaohongshu Images Skill

A Claude Code skill that transforms markdown, HTML, or text content into beautifully styled HTML pages with AI-generated cover images, then captures them as sequential screenshots at 3:4 ratio for Xiaohongshu posting.

## Features

- **Content Processing**: Accepts markdown, HTML, or plain text content
- **AI Cover Images**: Generates editorial-style cover illustrations using Google Gemini
- **Styled HTML Output**: Creates beautifully formatted HTML pages with modern typography
- **Screenshot Capture**: Takes sequential 3:4 ratio screenshots optimized for Xiaohongshu
- **Smart Text Boundaries**: Ensures no text is cut off in screenshots

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Code CLI

### Setup

1. **Clone or copy this skill to your Claude skills directory:**

```bash
# Copy to global skills
cp -r xiaohongshu-images-skill ~/.claude/skills/

# Or symlink for development
ln -s /path/to/xiaohongshu-images-skill ~/.claude/skills/xiaohongshu-images-skill
```

2. **Install Python dependencies:**

```bash
pip install python-dotenv playwright
playwright install chromium
```

3. **Configure environment variables:**

```bash
cd ~/.claude/skills/xiaohongshu-images-skill
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Get your Gemini API Key:**

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to obtain your API key.

## Usage

### Via Claude Code

Invoke the skill in Claude Code:

```
/xiaohongshu-images
```

Then provide your content:
- Paste markdown/HTML content directly
- Provide a file path: `/path/to/article.md`
- Provide a URL to fetch content from

### Example

```markdown
/xiaohongshu-images

# My Article Title

This is the introduction paragraph explaining the topic...

## Section 1

Content for section 1 with detailed explanation...

## Section 2

More content here with examples...
```

### Output

The skill generates output in `~/Dev/obsidian/articles/<date-title>/`:
- `xhs-preview.html` - Styled HTML preview page
- `_attachments/cover-xhs.png` - AI-generated cover image
- `_attachments/xhs-01.png, xhs-02.png, ...` - Sequential screenshots

## Directory Structure

```
xiaohongshu-images-skill/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── prompts/
│   └── default.md        # Default HTML/CSS styling prompt
├── scripts/
│   ├── generate_images.py    # Gemini image generation
│   └── screenshot.py         # Screenshot capture
├── .env                  # Environment variables (gitignored)
├── .env.example          # Environment template
└── .gitignore

Output directory (outside skill folder):
~/Dev/obsidian/articles/<date>-<title>/
├── xhs-preview.html          # Styled HTML preview page
├── prompts.json              # Image generation prompts
└── _attachments/             # Obsidian-style attachments folder
    ├── cover-xhs.png         # AI-generated cover image
    ├── xhs-01.png            # Screenshot page 1
    ├── xhs-02.png            # Screenshot page 2
    └── ...
```

## Customization

### Custom Prompt Templates

Create custom styling templates in the `prompts/` directory:

1. Create a new `.md` file (e.g., `prompts/minimal.md`)
2. Define your HTML/CSS specifications
3. Invoke with: "Use the minimal template for this article"

### Modifying Styles

Edit `prompts/default.md` to customize:
- Card dimensions and colors
- Font families and sizes
- Typography hierarchy
- Code block styling
- Responsive breakpoints

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for image generation | Yes |

### Screenshot Settings

Default screenshot dimensions (3:4 ratio for Xiaohongshu):
- Width: 1080px
- Height: 1440px
- Scale factor: 2x (Retina quality)

To modify, edit `scripts/screenshot.py`:
```python
SCREENSHOT_WIDTH = 1080
SCREENSHOT_HEIGHT = 1440
```

## Scripts

### generate_images.py

Generates cover images using Google Gemini API.

```bash
python scripts/generate_images.py ~/Dev/obsidian/articles/<date>-<title>/prompts.json
```

JSON format:
```json
{
    "theme": "Article theme for cover image generation"
}
```

Output: `~/Dev/obsidian/articles/<date>-<title>/_attachments/cover-xhs.png`

### screenshot.py

Captures sequential screenshots of HTML pages.

```bash
python scripts/screenshot.py ~/Dev/obsidian/articles/<date>-<title>/xhs-preview.html
```

Output: `~/Dev/obsidian/articles/<date>-<title>/_attachments/xhs-01.png`, `xhs-02.png`, etc.

Features:
- Automatic page scrolling
- Smart text boundary detection
- No text cut-off at boundaries
- 3:4 aspect ratio output

## Troubleshooting

### Gemini API Issues

- Verify your API key is correctly set in `.env`
- Check API quotas at [Google AI Studio](https://aistudio.google.com/)
- Ensure the API key has access to image generation models

### Screenshot Issues

- Install Playwright browsers: `playwright install chromium`
- Check file paths are correct
- Ensure HTML file is valid and accessible

### Font Loading

If fonts don't load in screenshots:
- Increase wait time in `screenshot.py`
- Check Google Fonts availability
- Consider using local fonts

## License

MIT License - See LICENSE file for details.

## Related Skills

- `chinese-viral-writer` - Chinese viral content creation
- `wechat-article-formatter` - WeChat article formatting
- `wechat-article-publisher` - WeChat publishing automation
