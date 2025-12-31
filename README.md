# Capcat - Personal News Archiving Utility

A powerful, modular news article archiving system that fetches articles from 12 sources, converts them to Markdown and HTML with themes for sharing, and organizes them with media files.

## Features

- **Smart Content Extraction**: Fetches articles from 12 news sources with intelligent content recovery
- **Fallback Image Detection**: Automatically finds content images when primary extraction misses them
- **Separated Workflows**: Independent article and comment processing for better reliability
- **Advanced Media Handling**: Downloads and embeds images (always), plus PDFs, audio, video with --media flag
- **Privacy-Compliant Comments**: User anonymization with profile link preservation
- **Hybrid Architecture**: 94.6% code reduction with config-driven + custom source support
- **Professional Output**: Structured folder hierarchy with date-based organization
- **Cross-Platform Compatibility**: Works reliably on Windows, macOS, and Linux
- **Parallel Processing**: Up to 8 concurrent workers for improved performance
- **HTML Generation**: Professional templates with consistent navigation

## Privacy & Ethics

**Capcat respects user privacy and follows ethical data practices:**

- **No Personal Data Collection**: Usernames are anonymized as "Anonymous" in all comment sections
- **Profile Link Preservation**: Original profile links to source websites are preserved for reference
- **Legal Compliance**: Meets privacy requirements by not storing personal identifying information
- **Transparency**: Only publicly available article content is archived, no private data harvesting
- **Source Attribution**: All content properly attributed to original sources with functioning links

## Advanced Content Processing

### Fallback Image Detection System

**Automatic Smart Recovery**: When the primary content extraction finds few images, Capcat automatically activates a comprehensive fallback system that:

- **Scans Full Pages**: Analyzes entire original HTML before filtering
- **Intelligent Filtering**: Removes UI elements (logos, ads, navigation) using 50+ patterns
- **Size Filtering**: Skips small images (< 150px) likely to be icons or decorative
- **Duplicate Prevention**: Avoids re-downloading existing images
- **Seamless Integration**: Adds found images as "Additional Images" section

**Example Output**:
```markdown
# Article Title

Original article content...

## Additional Images

*The following images were found using comprehensive page scanning:*

![Additional Image 1](images/content-image1.jpg)
![Additional Image 2](images/content-image2.png)
```

### Separated Article and Comment Workflows

**Clean Architecture**: Articles and comments are processed independently for better:

- **Reliability**: Comment failures don't break article downloads
- **Performance**: Parallel processing possible
- **Maintainability**: Clear separation of concerns
- **Error Isolation**: Each workflow handles its own error domain

**Benefits for Users**:
- Articles always save successfully, even if comments fail
- Faster processing through independent workflows
- Better error messages and recovery

## Improved Directory Structure (UX Enhancement)

Starting with the latest version, Capcat now separates application code from user content for better organization:

```
/Application/                 # Application code and executable (this directory)
  capcat.py                  # Main application
  core/                        # Core modules
  sources/                     # Source-specific modules
  requirements.txt             # Dependencies
  README.md                    # Documentation
  
/News/                        # User content (created when app runs)
  news_02-09-2025/             # Date-stamped content folder
    Hacker-News_02-09-2025/    # Hacker News articles
    Lobsters_02-09-2025/       # Lobsters articles
    InfoQ_02-09-2025/          # InfoQ articles
```

This separation means:
1. Application updates won't interfere with your downloaded content
2. Content is stored outside the application directory for cleaner organization
3. You can easily backup or move your content separately from the application

## Project Structure

- `capcat.py`: The main entry point for the application.
- `cli.py`: Handles command-line argument parsing and user interaction.
- `sources/`: Directory containing source-specific scanning logic.
  - `hn.py`: Module for scanning Hacker News.
  - `lb.py`: Module for scanning Lobsters.
  - `iq.py`: Module for scanning InfoQ with enhanced features.
- `core/`: Directory containing shared/core logic.
  - `downloader.py`: Handles downloading articles, images, and other media.
  - `formatter.py`: Converts HTML content to Markdown with enhanced cleanup.
  - `utils.py`: Utility functions for file handling, URL processing, etc.
  - `article_fetcher.py`: Base class for article fetching with shared functionality.

## Dependencies

- Python 3.7+
- `requests`
- `beautifulsoup4`
- `PyYAML`

## Installation

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python capcat.py --help
```

To scan articles:

```bash
# Scan top 30 from all sources (Hacker News, Lobsters, and InfoQ)
python capcat.py

# Scan top 10 from Hacker News only
python capcat.py --source hn --count 10

# Scan from Lobsters only, output to a specific directory
python capcat.py --source lb -o /path/to/output

# Scan from InfoQ only
python capcat.py --source iq --count 15

# Scan top 20 from all sources
python capcat.py --count 20

# Scan from specific sources using direct flags
python capcat.py --hn --lb --count 10
python capcat.py --iq --count 5
```

## Enhanced InfoQ Support

The InfoQ source module has been enhanced with several improvements:

1. **Better Article Scanning**: Uses more specific selectors to accurately target InfoQ articles
2. **Enhanced Metadata Extraction**: Improved extraction of author information and publication dates
3. **Audio Content Detection**: Better detection and handling of InfoQ's audio versions of articles
4. **Improved Media Processing**: Enhanced downloading and organization of images and other media
5. **Content Cleanup**: Better removal of tracking elements and branding content

## Output Structure

The tool creates a folder structure like this:

```
news_DD-MM-YYYY/
├── Hacker-News_DD-MM-YYYY/ (if Hacker News is fetched)
│   ├── 01_Article_Title_1/
│   │   ├── article.md
│   │   ├── comments.md
│   │   ├── images/
│   │   │   ├── image1.jpg
│   │   │   └── image2.png
│   │   └── files/
│   │       └── document1.pdf
│   └── ...
├── lb_DD-MM-YYYY/ (if Lobsters is fetched)
│   ├── 01_Article_Title_1/
│   │   ├── article.md
│   │   ├── comments.md
│   │   ├── images/
│   │   │   ├── image1.jpg
│   │   │   └── image2.png
│   │   └── files/
│   │       └── document1.pdf
│   └── ...
├── iq_DD-MM-YYYY/ (if InfoQ is fetched)
│   ├── 01_Article_Title_1/
│   │   ├── article.md
│   │   ├── images/
│   │   │   ├── image1.jpg
│   │   │   └── image2.png
│   │   ├── audio/
│   │   │   └── audio1.mp3 (if audio version available)
│   │   └── files/
│   │       └── document1.pdf
│   └── ...
```

## Testing

The application includes comprehensive tests to ensure functionality:

```bash
# Run all tests
python test_capcat.py
python test_article_structure.py
python test_audio_video.py
python test_infoq.py
python test_enhanced_infoq.py
python test_enhanced_formatter.py

# Run specific test
python test_infoq.py  # Tests InfoQ-specific functionality
```

## Configuration

Capcat can be configured through:
1. Command-line arguments
2. Environment variables
3. Configuration files (YAML or JSON)

Example configuration file (capcat.yml):
```yaml
network:
  connect_timeout: 10
  read_timeout: 8
  user_agent: "Mozilla/5.0 (compatible; Capcat/1.0)"
  
processing:
  max_workers: 8
  download_images: true
  download_videos: true
  download_audio: true
  download_documents: true
  
logging:
  default_level: "INFO"
  use_colors: true
```

Environment variables:
```bash
export CAPCAT_MAX_WORKERS=10
export CAPCAT_DOWNLOAD_IMAGES=true
export CAPCAT_USER_AGENT="Custom User Agent"
```