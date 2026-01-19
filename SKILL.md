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
5. **Save Output**: Saves the HTML to `~/Dev/obsidian/articles/<date-article-title>/xhs-preview.html`
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

Create the output folder path as: `~/Dev/obsidian/articles/<date>-<sanitized-title>/`
- Replace spaces with hyphens
- Remove special characters
- Keep the title reasonably short (max 50 characters)
- All images go in `_attachments/` subfolder

### Step 4: Generate Cover Image with Gemini

**⚠️ COMPLIANCE CHECK**: Before generating, ensure the image concept complies with Xiaohongshu community guidelines (Section 11 of the prompt template). The image must:
- Be age-appropriate with no revealing clothing or suggestive poses
- Avoid political symbols, violence, gambling, smoking, or alcohol abuse
- Convey positive, constructive messages
- Be culturally sensitive and original

If the prompt template specifies image generation requirements (which it does by default):

1. **Read the environment variables** from `{{SKILL_DIR}}/.env` to get `GEMINI_API_KEY`
2. **Analyze the article content** to extract the main theme
3. **Verify compliance** with community guidelines before proceeding
4. **Generate image prompt** based on the template:
   - Style: Hand-drawn illustration similar to *The New Yorker* editorial cartoons
   - Content: Visual representation of the article's main theme
   - Dimensions: 600px × 350px (will be scaled to fit)

4. **Call Gemini API** using the generate_images.py script:

```bash
cd {{SKILL_DIR}} && python scripts/generate_images.py ~/Dev/obsidian/articles/<date>-<title>/prompts.json
```

Or use direct API call via curl:

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=${GEMINI_API_KEY}" \
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

5. **Save the generated image** to `~/Dev/obsidian/articles/<date>-<title>/_attachments/cover-xhs.png`

### Step 5: Generate HTML

**⚠️ COMPLIANCE CHECK**: Before generating HTML, review the text content for compliance:
- No absolute/superlative claims (最好、第一、国家级、最高级、全网最低价)
- No exaggerated effect claims (一分钟见效、吃完就变白)
- No false or unverified medical/financial advice
- No defamatory or offensive language
- If health/investment topics are involved, add disclaimer text

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
        <img src="_attachments/cover-xhs.png" class="cover-image" alt="Cover">
        <div class="content">
            <!-- Article content -->
        </div>
    </div>
</body>
</html>
```

4. **Save the HTML** to `~/Dev/obsidian/articles/<date>-<title>/xhs-preview.html`

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
6. **Save screenshots** to `~/Dev/obsidian/articles/<date>-<title>/_attachments/`:
   - Sequential naming: `xhs-01.png`, `xhs-02.png`, `xhs-03.png`, etc.

**Use the screenshot script:**

```bash
cd {{SKILL_DIR}} && python scripts/screenshot.py ~/Dev/obsidian/articles/<date>-<title>/xhs-preview.html
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
├── .env                  # Environment variables (gitignored)
├── .env.example          # Environment variable template
└── .gitignore

Output directory (outside skill folder):
~/Dev/obsidian/articles/<date>-<title>/
├── xhs-preview.html          # Styled HTML preview page
├── prompts.json              # Image generation prompts
└── _attachments/             # Obsidian-style attachments folder
    ├── cover-xhs.png         # Cover image (600×350, scaled)
    ├── xhs-01.png            # Screenshot page 1 (1200×1600)
    ├── xhs-02.png            # Screenshot page 2
    └── ...
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
3. Create output folder: `~/Dev/obsidian/articles/2024-01-14-my-article-title/`
4. Generate cover image using Gemini API based on article theme
5. Save cover image to `~/Dev/obsidian/articles/2024-01-14-my-article-title/_attachments/cover-xhs.png`
6. Generate styled HTML following template specifications
7. Save to `~/Dev/obsidian/articles/2024-01-14-my-article-title/xhs-preview.html`
8. Open in browser and take 3:4 ratio screenshots
9. Save screenshots to `~/Dev/obsidian/articles/2024-01-14-my-article-title/_attachments/xhs-01.png`, etc.
10. Report completion with file locations

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

## Community Compliance (社区规范合规)

**IMPORTANT**: All generated content must comply with Xiaohongshu community guidelines.

### Quick Reference - Prohibited Content:

| Category | Examples | Action |
|----------|----------|--------|
| Absolute claims | 最好、最佳、第一、国家级 | Remove or rephrase |
| Exaggerated effects | 一分钟见效、立刻瘦10斤 | Remove or add disclaimers |
| Medical/Financial advice | Health tips, investment suggestions | Add disclaimer: "本内容不构成医疗/投资建议" |
| Inappropriate imagery | Nudity, violence, political symbols | Regenerate with appropriate content |
| False information | Pseudoscience, unverified claims | Verify or remove |
| Defamatory content | Attacks on brands/individuals | Remove entirely |

### Official Guidelines:

- 社区规范: https://www.xiaohongshu.com/crown/community/rules
- 社区公约: https://www.xiaohongshu.com/crown/community/agreement

### Compliance Workflow:

1. **Before image generation**: Review theme for appropriateness
2. **Before HTML generation**: Scan text for prohibited phrases
3. **Before final output**: Run through compliance checklist in prompt template (Section 11.5)
