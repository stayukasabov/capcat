# Advanced Image Filtering

Sophisticated image filtering strategies for config-driven sources to handle complex website layouts with unwanted images (related articles, ads, thumbnails).

## Overview

Capcat provides multi-layered image filtering to extract only relevant article images:

1. **CSS Selector Filtering** - Extract images from specific containers
2. **Skip Selectors** - Exclude images in unwanted sections
3. **URL Pattern Filtering** - Only download images from specific domains
4. **Count Limiting** - Limit to first N images
5. **Size Filtering** - Filter by minimum file size

## Configuration Options

### Basic Configuration

```yaml
image_processing:
  # Where to find images
  selectors:
    - "article img"
    - ".content img"

  # Which domains to allow
  url_patterns:
    - "example.com"
    - "cdn.example.com"
```

### Skip Selectors

Exclude images in specific containers (e.g., related articles, sidebars, ads):

```yaml
image_processing:
  skip_selectors:
    - ".sidebar img"              # Sidebar images
    - ".navigation img"           # Navigation/header images
    - ".related-articles img"     # Related article thumbnails
    - ".advertisement img"        # Ad images
    - ".author-bio img"           # Author avatars
```

**How it works:** During extraction, images with parents matching skip selectors are excluded.

**Syntax:**
- `".class-name img"` - Skip images inside elements with class
- `"tag img"` - Skip images inside specific HTML tags
- `"#id img"` - Skip images inside element with ID

### Max Images Limit

Limit to first N images (applied AFTER skip_selectors):

```yaml
image_processing:
  max_images: 3  # Only download first 3 images
```

**Use cases:**
- News sites with 1-2 main article images + many related article thumbnails
- Reduce download time/bandwidth
- Focus on primary visual content

**Example:** MIT News articles have 1-2 main images + 60+ related article thumbnails. Setting `max_images: 3` extracts only main article images.

### Minimum Image Size

Filter out small images (icons, thumbnails, tracking pixels):

```yaml
image_processing:
  min_image_size: 10240  # 10KB minimum
```

**Size thresholds:**
- `5120` (5KB) - Filter tiny icons/favicons
- `10240` (10KB) - Standard threshold for thumbnails
- `20480` (20KB) - Aggressive filtering, only large images

**How it works:**
1. Checks `Content-Length` header before download
2. If unavailable, downloads and verifies size
3. Removes file if below threshold

## Filtering Strategy

Filters are applied in this order:

```
1. Extract images using selectors
   ↓
2. Apply skip_selectors (remove unwanted containers)
   ↓
3. Apply URL pattern filtering
   ↓
4. Apply max_images limit
   ↓
5. Download with min_image_size filtering
```

## Real-World Examples

### MIT News AI

**Problem:** Articles have 1-2 main images but 60+ related article thumbnails in `.news-article--recent-news` sections.

**Solution:**
```yaml
image_processing:
  selectors:
    - "article img"
    - ".news-article img"

  url_patterns:
    - "news.mit.edu"
    - "mit.edu"

  skip_selectors:
    - ".news-article--recent-news img"  # Skip related articles

  max_images: 3           # Limit to first 3 images
  min_image_size: 10240   # 10KB minimum
```

**Result:** Extracts 1-3 main article images, skips all related article thumbnails.

### News Site with Sidebar Ads

**Problem:** Articles have 2-3 content images but also sidebar ads and related article thumbnails.

**Solution:**
```yaml
image_processing:
  selectors:
    - ".article-body img"

  skip_selectors:
    - ".sidebar img"
    - ".advertisement img"
    - ".related-posts img"
    - ".author-card img"

  max_images: 5
  min_image_size: 15360  # 15KB minimum
```

### Blog with Large Image Galleries

**Problem:** Some posts have 20+ images in galleries, want only hero image.

**Solution:**
```yaml
image_processing:
  selectors:
    - ".hero-image img"
    - ".featured-image img"

  max_images: 1  # Only first image
```

## Testing Image Filtering

### Test Your Configuration

```bash
# Fetch single article to test
./capcat fetch sourcename --count 1

# Check downloaded images
ls -lh ../News/news_*/SourceName_*/*/images/

# Verify image count and sizes
find ../News/news_*/SourceName_* -name "*.jpg" -exec ls -lh {} \;
```

### Debug Logging

Enable debug logging to see filtering in action:

```bash
./capcat -L capcat.log fetch sourcename --count 1
grep -i "image\|skip\|limit" capcat.log
```

## Best Practices

1. **Start broad, then narrow**
   - Begin with general selectors
   - Add skip_selectors for unwanted sections
   - Add max_images if still too many

2. **Use browser DevTools**
   - Inspect page HTML structure
   - Identify CSS classes for unwanted image containers
   - Test selectors in browser console

3. **Test with multiple articles**
   - Page layouts vary between articles
   - Verify filtering works across different article types

4. **Balance quality vs quantity**
   - `max_images: 1` for hero images only
   - `max_images: 3-5` for comprehensive coverage
   - `max_images: 10+` for image-heavy content

5. **Combine multiple strategies**
   - Use skip_selectors for structural filtering
   - Use max_images for count limits
   - Use min_image_size for quality filtering

## Common Patterns

### Related Articles Section
```yaml
skip_selectors:
  - ".related-articles img"
  - ".also-read img"
  - ".more-stories img"
  - ".recommended img"
```

### Sidebar/Navigation
```yaml
skip_selectors:
  - ".sidebar img"
  - "aside img"
  - "nav img"
  - ".header img"
  - ".footer img"
```

### Ads/Sponsored Content
```yaml
skip_selectors:
  - ".advertisement img"
  - ".sponsored img"
  - ".promoted img"
  - "[class*='ad-'] img"
```

### User Profile/Author Images
```yaml
skip_selectors:
  - ".author-bio img"
  - ".user-avatar img"
  - ".profile-pic img"
  - ".byline img"
```

## Troubleshooting

### Too many images downloaded
- Add skip_selectors for unwanted sections
- Reduce max_images value
- Increase min_image_size threshold

### Missing important images
- Check skip_selectors aren't too broad
- Verify selectors target correct containers
- Check URL patterns allow image CDN domains
- Lower min_image_size threshold

### Downloading placeholders
- Ensure data-src prioritization (lazy loading)
- Check URL patterns include actual image domains
- Verify images aren't in skipped containers

## Performance Impact

- **skip_selectors**: Minimal (processed during extraction)
- **max_images**: Minimal (simple list slicing)
- **min_image_size**: Adds HEAD request per image (~50-100ms each)

For optimal performance, prefer skip_selectors and max_images over min_image_size when possible.
