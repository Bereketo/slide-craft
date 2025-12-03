# Cover Image Description Generator

This script uses AI (OpenAI's GPT-4 Vision) to automatically generate descriptions for all cover images to help users choose the right cover based on content, theme, colors, and mood.

## Setup

### 1. Install Required Package

```bash
pip install openai
```

### 2. Set Your OpenAI API Key

You need an OpenAI API key with access to GPT-4 Vision (gpt-4o or gpt-4-vision-preview).

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Option B: Add to your shell profile**
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### Basic Usage (Process All Covers)

```bash
python extras/generate_cover_descriptions.py
```

### Test with Limited Covers

To test with just the first 5 covers before processing all 75:

Edit the script and change:
```python
limit=5  # Instead of limit=None
```

Then run:
```bash
python extras/generate_cover_descriptions.py
```

### Resume from a Specific Cover

If the script stops midway, you can resume from a specific cover:

Edit the script and change:
```python
start_from=20  # Resume from cover 20
```

## What It Does

For each cover image, the script:

1. **Analyzes** the image using GPT-4 Vision
2. **Generates** a 2-3 sentence description including:
   - Main subject/theme (e.g., business meeting, technology, nature)
   - Dominant colors and mood (e.g., professional blue, warm and energetic)
   - Best use case (e.g., suitable for corporate presentations, tech startups)
3. **Updates** the `description` field in `/branding/covers/index.json`

## Example Output

Before:
```json
{
  "id": 1,
  "image": "cover_01.jpg",
  "description": "Standard title with subtitle"
}
```

After:
```json
{
  "id": 1,
  "image": "cover_01.jpg",
  "description": "Modern office workspace with laptop and coffee, featuring cool blue and neutral tones. Professional and clean aesthetic, perfect for business presentations, corporate reports, or technology-related content."
}
```

## Cost Estimation

- Model: GPT-4o with vision (low detail mode)
- Approximate cost: ~$0.01 per image
- Total for 75 covers: ~$0.75

## Configuration Options

In the `main()` function, you can adjust:

```python
update_index_with_descriptions(
    index_path=index_path,
    images_dir=images_dir,
    api_key=api_key,
    start_from=1,      # Which cover to start from
    limit=None         # How many to process (None = all)
)
```

## Rate Limiting

The script includes a 0.5-second delay between API calls to avoid rate limits. Adjust in the code if needed:

```python
time.sleep(0.5)  # Increase if you hit rate limits
```

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"
- Make sure you've exported your API key
- Check with: `echo $OPENAI_API_KEY`

### "Image not found"
- Verify images are in `/branding/covers/images/`
- Check filename matches what's in index.json

### API Rate Limit Errors
- Increase the `time.sleep()` delay
- Process covers in batches using `limit` parameter

### Model Not Available
- Check your OpenAI account has access to GPT-4 Vision
- Try changing model from `gpt-4o` to `gpt-4-vision-preview`

## Alternative: Use Local Models

If you prefer not to use OpenAI, you can modify the script to use:
- **Ollama** with LLaVA model (free, runs locally)
- **Anthropic Claude 3** with vision
- **Google Gemini Pro Vision**

Let me know if you need a version for any of these alternatives!

