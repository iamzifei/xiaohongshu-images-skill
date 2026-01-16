---
name: xiaohongshu-images
description: Transform markdown/HTML into styled 3:4 ratio images for Xiaohongshu
---

# Xiaohongshu Images Skill

This skill transforms markdown, HTML, or text content into beautifully styled HTML pages with AI-generated cover images, then captures them as sequential screenshots at 3:4 ratio for Xiaohongshu posting.

## Overview

The skill performs the following workflow:

1. **Accept Content**: Receives markdown, HTML, or txt format content from the user
2. **Load Prompt Template**: Reads the prompt template from `prompts/default.md` in this skill's directory
3. **Generate Cover Image**: Uses Gemini API to generate a cover image based on the article content
4. **Generate HTML**: Creates a beautifully styled HTML page following the prompt template specifications
5. **Save Output**: Saves the HTML to `/output/<date-article-title>/index.html`
6. **Capture Screenshots**: Takes sequential 3:4 ratio screenshots of the entire page without cutting text

## Usage

When the user invokes this skill, follow these steps:

### Step 1: Identify the Input

The user will provide one of the following:
- A file path to a markdown, HTML, or txt file (e.g., `/path/to/article.md`)
- Raw content directly in the conversation
- A URL to fetch content from

If the input is unclear, ask the user to provide either a file path, URL, or paste the content directly.

### Step 2: Read the Prompt Template

Read the prompt template from this skill's directory:

```
{{SKILL_DIR}}/prompts/default.md
```

Use the Read tool to get the prompt template content. This template defines the HTML/CSS styling specifications.

### Step 3: Extract Article Title and Date

From the content, extract:
- **Title**: The main heading (h1) or first significant title in the content
- **Date**: Current date in YYYY-MM-DD format

Create the output folder name as: `<date>-<sanitized-title>`
- Replace spaces with hyphens
- Remove special characters
- Keep it reasonably short (max 50 characters)

### Step 4: Generate Cover Image with Gemini

If the prompt template specifies image generation requirements (which it does by default):

1. **Read the environment variables** from `{{SKILL_DIR}}/.env` to get `GEMINI_API_KEY`
2. **Analyze the article content** to extract the main theme
3. **Generate image prompt** based on the template:
   - Style: Hand-drawn illustration similar to *The New Yorker* editorial cartoons
   - Content: Visual representation of the article's main theme
   - Dimensions: 600px × 350px (will be scaled to fit)

4. **Call Gemini API** using the generate_images.py script:

```bash
cd {{SKILL_DIR}} && python scripts/generate_images.py output/<folder-name>/prompts.json
```

Or use direct API call via curl:

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{"text": "<image_prompt>"}]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

5. **Save the generated image** to `output/<folder-name>/images/cover.png`

### Step 5: Generate HTML

Using the prompt template and the user's content:

1. **Parse the content** to identify:
   - Title (h1)
   - Subtitles (h2-h6)
   - Paragraphs
   - Lists
   - Code blocks
   - Links
   - Emphasis/bold text
   - Blockquotes

2. **Generate complete HTML** following the template specifications:
   - Dark gradient background
   - 600px × 800px cream-colored card
   - Proper typography with Google Fonts (Noto Serif SC, Inter, JetBrains Mono)
   - Cover image at the top
   - All specified styling for text, links, lists, code blocks, etc.
   - Responsive design for mobile

3. **Important HTML Structure**:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Title</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700&family=Inter:wght@300;400;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* All CSS styles inline */
    </style>
</head>
<body>
    <div class="container">
        <img src="images/cover.png" class="cover-image" alt="Cover">
        <div class="content">
            <!-- Article content -->
        </div>
    </div>
</body>
</html>
```

4. **Save the HTML** to `output/<folder-name>/index.html`

### Step 6: Take Screenshots

After generating the HTML, capture sequential screenshots of the `.container` element at **exact 3:4 aspect ratio**:

**Screenshot Specifications:**
- Container viewport: 600px × 800px (3:4 ratio)
- Output resolution: 1200px × 1600px (2x device scale factor)
- Each screenshot captures exactly the `.container` element, not the full page

**Capture Process:**

1. **Open the HTML page** using Playwright browser with viewport larger than container
2. **Configure browser context**:
   - Viewport: 800px × 1000px (larger than container to ensure full visibility)
   - Device scale factor: 2x for high-resolution output
3. **Scroll within the container**:
   - The `.container` element has `overflow-y: auto`, making it internally scrollable
   - Start from `scrollTop = 0` and increment through the content
   - Each scroll position captures one 3:4 ratio screenshot
4. **Smart text boundary detection**:
   - Before each screenshot, analyze visible block elements (p, h1-h6, li, blockquote, pre, img)
   - If an element would be cut at the bottom boundary, end the current screenshot before that element
   - Add whitespace mask to cover partial content, maintaining clean 3:4 frame
   - Next screenshot starts with the cut element at the top
5. **Capture the complete `.container` content**:
   - Use `container.screenshot()` to capture only the container element (excludes page background)
   - Continue until all content is captured (scrollTop reaches scrollHeight - clientHeight)
6. **Save screenshots** to `output/<folder-name>/screenshots/`:
   - Sequential naming: `01.png`, `02.png`, `03.png`, etc.

**Use the screenshot script:**

```bash
cd {{SKILL_DIR}} && python scripts/screenshot.py output/<folder-name>/index.html
```

**Script Output:**
- Each screenshot: exactly 1200×1600 pixels (3:4 ratio at 2x scale)
- Only the cream-colored card content is captured
- No text is cut off between screenshots

### Step 7: Report Results

After completion, report to the user:
- HTML file location
- Number of screenshots generated
- Screenshots folder location
- Preview of the first screenshot (if possible)

## Directory Structure

```
{{SKILL_DIR}}/
├── SKILL.md              # This file
├── prompts/
│   └── default.md        # Default HTML/CSS styling prompt
├── scripts/
│   ├── generate_images.py    # Gemini image generation script
│   └── screenshot.py         # Screenshot capture script
├── output/               # Generated outputs (gitignored)
│   └── <date-title>/
│       ├── index.html
│       ├── images/
│       │   └── cover.png
│       └── screenshots/
│           ├── 01.png
│           ├── 02.png
│           └── ...
├── .env                  # Environment variables (gitignored)
├── .env.example          # Environment variable template
└── .gitignore
```

## Environment Variables

Required environment variables in `.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: https://aistudio.google.com/app/apikey

## Example Workflow

**User:** Create a styled article page from this markdown:

```markdown
# My Article Title

This is the introduction paragraph...

## Section 1

Content for section 1...
```

**Assistant Actions:**
1. Read prompt template from `prompts/default.md`
2. Extract title: "My Article Title"
3. Create output folder: `output/2024-01-14-my-article-title/`
4. Generate cover image using Gemini API based on article theme
5. Generate styled HTML following template specifications
6. Save to `output/2024-01-14-my-article-title/index.html`
7. Open in browser and take 3:4 ratio screenshots
8. Save screenshots to `output/2024-01-14-my-article-title/screenshots/`
9. Report completion with file locations

## Custom Prompt Templates

Users can provide custom prompt templates by:
1. Placing a `.md` file in the `prompts/` directory
2. Specifying the template name when invoking the skill

Example: "Use the `xiaohongshu-style` template for this article"

## Error Handling

If the Gemini API call fails:
1. Display the error message to the user
2. Offer to retry or proceed without cover image
3. If proceeding without image, use a placeholder or omit the cover

If screenshot capture fails:
1. Verify the HTML file exists and is valid
2. Check browser dependencies
3. Report the specific error to the user

## Dependencies

This skill requires:
- Python 3.8+
- `python-dotenv` package
- Playwright for screenshot capture (installed via pip: `pip install playwright && playwright install chromium`)

Install dependencies:

```bash
pip install python-dotenv playwright
playwright install chromium
```

## Notes

- The skill preserves all original content exactly as provided
- No modifications, simplifications, or deletions to the content
- The cover image is generated based on the article's main theme
- Screenshots are optimized for Xiaohongshu's 3:4 aspect ratio
- Text is never cut off in screenshots - boundaries are adjusted intelligently
