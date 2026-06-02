#!/usr/bin/env python3
"""
Generate Architecture Diagrams for Capcat

Creates Mermaid diagrams for system architecture, data flow, and component relationships.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List


class DiagramGenerator:
    """Generates various architectural diagrams."""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.diagrams_dir = self.output_dir / "diagrams"
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_diagrams(self) -> None:
        """Generate all architecture diagrams."""
        print("Generating system architecture diagram...")
        self.generate_system_architecture()

        print("Generating data flow diagram...")
        self.generate_data_flow()

        print("Generating source system diagram...")
        self.generate_source_system()

        print("Generating processing pipeline diagram...")
        self.generate_processing_pipeline()

        print("Generating deployment diagram...")
        self.generate_deployment_diagram()

        print("Generating class diagrams...")
        self.generate_class_diagrams()

    def generate_system_architecture(self) -> None:
        """Generate overall system architecture diagram."""
        diagram = """# System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Interface<br/>cli.py]
        Wrapper[Bash Wrapper<br/>capcat]
        PythonWrapper[Python Wrapper<br/>run_capcat.py]
    end

    subgraph "Application Layer"
        Main[Main Application<br/>capcat.py]
        Config[Configuration<br/>core.config]
        ErrorHandler[Error Handling<br/>core.error_handling]
        Progress[Progress Tracking<br/>core.progress]
    end

    subgraph "Source Management"
        SourceFactory[Source Factory<br/>core.source_system.source_factory]
        SourceRegistry[Source Registry<br/>core.source_system.source_registry]
        BaseSource[Base Source<br/>core.source_system.base_source]

        subgraph "Source Types"
            ConfigDriven[Config-Driven Sources<br/>YAML-based]
            CustomSources[Custom Sources<br/>Python-based]
        end
    end

    subgraph "Processing Pipeline"
        ArticleFetcher[Article Fetcher<br/>core.article_fetcher]
        MediaProcessor[Media Processor<br/>core.unified_media_processor]
        ContentFormatter[Content Formatter<br/>core.formatter]
        HTMLGenerator[HTML Generator<br/>htmlgen/]
    end

    subgraph "Core Services"
        SessionPool[Session Pool<br/>core.session_pool]
        ImageProcessor[Image Processor<br/>core.image_processor]
        Downloader[Media Downloader<br/>core.downloader]
        Utils[Utilities<br/>core.utils]
    end

    subgraph "Output Layer"
        FileSystem[File System]
        MarkdownFiles[Markdown Files]
        MediaFiles[Media Files]
        HTMLFiles[HTML Files]
        Logging[Log Files]
    end

    %% User interactions
    CLI --> Main
    Wrapper --> Main
    PythonWrapper --> Main

    %% Application flow
    Main --> Config
    Main --> ErrorHandler
    Main --> Progress
    Main --> SourceFactory

    %% Source management
    SourceFactory --> SourceRegistry
    SourceRegistry --> BaseSource
    BaseSource --> ConfigDriven
    BaseSource --> CustomSources

    %% Processing flow
    SourceFactory --> ArticleFetcher
    ArticleFetcher --> MediaProcessor
    MediaProcessor --> ContentFormatter
    ContentFormatter --> HTMLGenerator

    %% Core services
    ArticleFetcher --> SessionPool
    MediaProcessor --> ImageProcessor
    MediaProcessor --> Downloader
    ArticleFetcher --> Utils
    MediaProcessor --> Utils

    %% Output
    ContentFormatter --> MarkdownFiles
    MediaProcessor --> MediaFiles
    HTMLGenerator --> HTMLFiles
    ErrorHandler --> Logging
    Progress --> Logging

    %% Styling
    classDef uiLayer fill:#e1f5fe
    classDef appLayer fill:#f3e5f5
    classDef sourceLayer fill:#e8f5e8
    classDef processLayer fill:#fff3e0
    classDef serviceLayer fill:#fce4ec
    classDef outputLayer fill:#f1f8e9

    class CLI,Wrapper,PythonWrapper uiLayer
    class Main,Config,ErrorHandler,Progress appLayer
    class SourceFactory,SourceRegistry,BaseSource,ConfigDriven,CustomSources sourceLayer
    class ArticleFetcher,MediaProcessor,ContentFormatter,HTMLGenerator processLayer
    class SessionPool,ImageProcessor,Downloader,Utils serviceLayer
    class FileSystem,MarkdownFiles,MediaFiles,HTMLFiles,Logging outputLayer
```

## Component Relationships

- **UI Layer**: Entry points for user interaction
- **Application Layer**: Core application logic and coordination
- **Source Management**: Modular source system with auto-discovery
- **Processing Pipeline**: Article content processing workflow
- **Core Services**: Shared utilities and services
- **Output Layer**: File system operations and data persistence
"""

        with open(self.diagrams_dir / "system_architecture.md", 'w') as f:
            f.write(diagram)

    def generate_data_flow(self) -> None:
        """Generate data flow diagram."""
        diagram = """# Data Flow Diagram

```mermaid
flowchart TD
    Start([User Command]) --> Parse[Parse CLI Arguments]
    Parse --> Validate[Validate Configuration]
    Validate --> LoadSources[Load Source Configurations]

    LoadSources --> SourceType{Source Type?}

    SourceType -->|Config-Driven| LoadYAML[Load YAML Config]
    SourceType -->|Custom| LoadPython[Load Python Module]

    LoadYAML --> CreateSource1[Create Config-Driven Source]
    LoadPython --> CreateSource2[Create Custom Source]

    CreateSource1 --> FetchArticles[Fetch Article List]
    CreateSource2 --> FetchArticles

    FetchArticles --> ProcessParallel{Process in Parallel}

    ProcessParallel --> FetchContent[Fetch Article Content]
    FetchContent --> ExtractMedia[Extract Media URLs]
    ExtractMedia --> DownloadMedia[Download Media Files]
    DownloadMedia --> ProcessImages[Process Images]
    ProcessImages --> ConvertHTML[Convert HTML to Markdown]
    ConvertHTML --> GenerateHTML[Generate HTML Output]

    GenerateHTML --> SaveFiles[Save to File System]

    SaveFiles --> UpdateProgress[Update Progress]
    UpdateProgress --> CheckComplete{All Articles Done?}

    CheckComplete -->|No| ProcessParallel
    CheckComplete -->|Yes| Complete[Complete]

    %% Error handling
    FetchContent --> Error{Error?}
    Error -->|Yes| LogError[Log Error]
    Error -->|No| ExtractMedia
    LogError --> CheckComplete

    %% Styling
    classDef startEnd fill:#4caf50,color:#fff
    classDef process fill:#2196f3,color:#fff
    classDef decision fill:#ff9800,color:#fff
    classDef error fill:#f44336,color:#fff

    class Start,Complete startEnd
    class Parse,Validate,LoadSources,LoadYAML,LoadPython,CreateSource1,CreateSource2,FetchArticles,FetchContent,ExtractMedia,DownloadMedia,ProcessImages,ConvertHTML,GenerateHTML,SaveFiles,UpdateProgress process
    class SourceType,ProcessParallel,CheckComplete,Error decision
    class LogError error
```

## Data Transformations

### 1. Input Processing
- **CLI Arguments** → **Configuration Object**
- **Source Names** → **Source Instances**
- **URLs** → **Article Metadata**

### 2. Content Processing
- **HTML Content** → **Cleaned HTML**
- **Cleaned HTML** → **Markdown Text**
- **Media URLs** → **Local File Paths**

### 3. Output Generation
- **Article Data** → **Markdown Files**
- **Media Content** → **Organized File Structure**
- **Article + Metadata** → **HTML Pages**

### 4. Error Handling
- **Network Errors** → **Retry Logic**
- **Parse Errors** → **Fallback Processing**
- **File Errors** → **Alternative Paths**
"""

        with open(self.diagrams_dir / "data_flow.md", 'w') as f:
            f.write(diagram)

    def generate_source_system(self) -> None:
        """Generate source system architecture diagram."""
        diagram = """# Source System Architecture

```mermaid
graph TB
    subgraph "Source Discovery"
        Scanner[Directory Scanner]
        YAMLLoader[YAML Config Loader]
        ModuleLoader[Python Module Loader]
        Validator[Source Validator]
    end

    subgraph "Source Registry"
        Registry[Source Registry<br/>Centralized source management]
        Metadata[Source Metadata<br/>name, type, capabilities]
        Cache[Registration Cache]
    end

    subgraph "Source Factory"
        Factory[Source Factory<br/>Creates source instances]
        TypeResolver[Type Resolver<br/>Determines source type]
        InstanceCreator[Instance Creator<br/>Instantiates sources]
    end

    subgraph "Base Source Interface"
        BaseSource[BaseSource Abstract Class]
        GetArticles[get_articles method]
        GetContent[get_article_content method]
        Validate[validate method]
    end

    subgraph "Config-Driven Sources"
        ConfigSchema[Configuration Schema]
        YAMLConfig[YAML Configuration Files]
        ConfigParser[Config Parser]
        GenericSource[Generic Source Implementation]

        subgraph "YAML Examples"
            InfoQ[InfoQ Config]
            IEEE[IEEE Config]
            Mashable[Mashable Config]
        end
    end

    subgraph "Custom Sources"
        CustomInterface[Custom Source Interface]
        PythonModules[Python Source Modules]
        SourceLogic[Custom Business Logic]

        subgraph "Custom Examples"
            HackerNews[Hacker News Source]
            BBC[BBC Source]
            Nature[Nature Source]
        end
    end

    %% Discovery flow
    Scanner --> YAMLLoader
    Scanner --> ModuleLoader
    YAMLLoader --> Validator
    ModuleLoader --> Validator
    Validator --> Registry

    %% Registry management
    Registry --> Metadata
    Registry --> Cache

    %% Factory creation
    Factory --> TypeResolver
    TypeResolver --> InstanceCreator
    Registry --> Factory

    %% Base interface
    InstanceCreator --> BaseSource
    BaseSource --> GetArticles
    BaseSource --> GetContent
    BaseSource --> Validate

    %% Config-driven implementation
    ConfigSchema --> YAMLConfig
    YAMLConfig --> ConfigParser
    ConfigParser --> GenericSource
    GenericSource --> BaseSource

    YAMLConfig --> InfoQ
    YAMLConfig --> IEEE
    YAMLConfig --> Mashable

    %% Custom implementation
    CustomInterface --> PythonModules
    PythonModules --> SourceLogic
    SourceLogic --> BaseSource

    PythonModules --> HackerNews
    PythonModules --> BBC
    PythonModules --> Nature

    %% Styling
    classDef discovery fill:#e3f2fd
    classDef registry fill:#f3e5f5
    classDef factory fill:#e8f5e8
    classDef interface fill:#fff3e0
    classDef config fill:#fce4ec
    classDef custom fill:#f1f8e9

    class Scanner,YAMLLoader,ModuleLoader,Validator discovery
    class Registry,Metadata,Cache registry
    class Factory,TypeResolver,InstanceCreator factory
    class BaseSource,GetArticles,GetContent,Validate interface
    class ConfigSchema,YAMLConfig,ConfigParser,GenericSource,InfoQ,IEEE,Mashable config
    class CustomInterface,PythonModules,SourceLogic,HackerNews,BBC,Nature custom
```

## Source Types Comparison

| Aspect | Config-Driven | Custom |
|--------|---------------|--------|
| **Setup Time** | 15-30 minutes | 2-4 hours |
| **Complexity** | Simple HTML parsing | Full Python implementation |
| **Flexibility** | Limited to CSS selectors | Complete control |
| **Maintenance** | YAML config updates | Code changes required |
| **Comments Support** | No | Yes |
| **Custom Logic** | No | Yes |
| **Examples** | InfoQ, IEEE, Mashable | HN, BBC, Nature |

## Source Registration Process

1. **Directory Scan**: Scan `sources/active/` directory
2. **Type Detection**: Identify config-driven vs custom sources
3. **Validation**: Validate configuration/implementation
4. **Registration**: Add to source registry with metadata
5. **Caching**: Store registration data for performance
"""

        with open(self.diagrams_dir / "source_system.md", 'w') as f:
            f.write(diagram)

    def generate_processing_pipeline(self) -> None:
        """Generate processing pipeline diagram."""
        diagram = """# Processing Pipeline

```mermaid
graph LR
    subgraph "Input Stage"
        URLs[Article URLs]
        Config[Processing Config]
        OutputDir[Output Directory]
    end

    subgraph "Fetch Stage"
        HttpRequest[HTTP Request]
        RateLimit[Rate Limiting]
        SessionPool[Session Pooling]
        RetryLogic[Retry Logic]
        ResponseValidation[Response Validation]
    end

    subgraph "Parse Stage"
        HTMLParser[HTML Parser]
        ContentExtraction[Content Extraction]
        MetadataExtraction[Metadata Extraction]
        LinkProcessing[Link Processing]
        CleanupHTML[HTML Cleanup]
    end

    subgraph "Media Stage"
        MediaDetection[Media Detection]
        URLExtraction[URL Extraction]
        TypeClassification[Type Classification]
        MediaDownload[Media Download]
        ImageProcessing[Image Processing]
        FileOrganization[File Organization]
    end

    subgraph "Conversion Stage"
        MarkdownConversion[Markdown Conversion]
        LinkUpdating[Link Updating]
        ImageEmbedding[Image Embedding]
        ContentStructuring[Content Structuring]
        MetadataInsertion[Metadata Insertion]
    end

    subgraph "HTML Generation Stage"
        TemplateLoading[Template Loading]
        ContentRendering[Content Rendering]
        StyleApplication[Style Application]
        NavigationGeneration[Navigation Generation]
        AssetLinking[Asset Linking]
    end

    subgraph "Output Stage"
        DirectoryCreation[Directory Creation]
        FileWriting[File Writing]
        PermissionSetting[Permission Setting]
        ProgressTracking[Progress Tracking]
        ErrorLogging[Error Logging]
    end

    %% Flow connections
    URLs --> HttpRequest
    Config --> RateLimit
    OutputDir --> DirectoryCreation

    HttpRequest --> RateLimit
    RateLimit --> SessionPool
    SessionPool --> RetryLogic
    RetryLogic --> ResponseValidation

    ResponseValidation --> HTMLParser
    HTMLParser --> ContentExtraction
    ContentExtraction --> MetadataExtraction
    MetadataExtraction --> LinkProcessing
    LinkProcessing --> CleanupHTML

    CleanupHTML --> MediaDetection
    MediaDetection --> URLExtraction
    URLExtraction --> TypeClassification
    TypeClassification --> MediaDownload
    MediaDownload --> ImageProcessing
    ImageProcessing --> FileOrganization

    CleanupHTML --> MarkdownConversion
    FileOrganization --> LinkUpdating
    MarkdownConversion --> LinkUpdating
    LinkUpdating --> ImageEmbedding
    ImageEmbedding --> ContentStructuring
    ContentStructuring --> MetadataInsertion

    MetadataInsertion --> TemplateLoading
    TemplateLoading --> ContentRendering
    ContentRendering --> StyleApplication
    StyleApplication --> NavigationGeneration
    NavigationGeneration --> AssetLinking

    MetadataInsertion --> DirectoryCreation
    AssetLinking --> FileWriting
    DirectoryCreation --> FileWriting
    FileWriting --> PermissionSetting
    PermissionSetting --> ProgressTracking

    %% Error handling
    RetryLogic -.-> ErrorLogging
    MediaDownload -.-> ErrorLogging
    FileWriting -.-> ErrorLogging

    %% Styling
    classDef input fill:#e3f2fd
    classDef fetch fill:#e8f5e8
    classDef parse fill:#fff3e0
    classDef media fill:#fce4ec
    classDef convert fill:#f3e5f5
    classDef html fill:#f1f8e9
    classDef output fill:#ffe0b2

    class URLs,Config,OutputDir input
    class HttpRequest,RateLimit,SessionPool,RetryLogic,ResponseValidation fetch
    class HTMLParser,ContentExtraction,MetadataExtraction,LinkProcessing,CleanupHTML parse
    class MediaDetection,URLExtraction,TypeClassification,MediaDownload,ImageProcessing,FileOrganization media
    class MarkdownConversion,LinkUpdating,ImageEmbedding,ContentStructuring,MetadataInsertion convert
    class TemplateLoading,ContentRendering,StyleApplication,NavigationGeneration,AssetLinking html
    class DirectoryCreation,FileWriting,PermissionSetting,ProgressTracking,ErrorLogging output
```

## Pipeline Performance Characteristics

### Parallel Processing
- **Article Fetching**: Up to 8 concurrent requests
- **Media Download**: Parallel image/media processing
- **File Operations**: Concurrent file writing

### Error Handling
- **Network Errors**: Exponential backoff retry
- **Parse Errors**: Graceful degradation
- **File Errors**: Alternative path resolution

### Resource Management
- **Memory**: Streaming for large files
- **Network**: Connection pooling and reuse
- **Disk**: Efficient directory structures

### Quality Controls
- **Content Validation**: HTML structure verification
- **Media Validation**: File type and size checks
- **Output Validation**: Markdown syntax verification
"""

        with open(self.diagrams_dir / "processing_pipeline.md", 'w') as f:
            f.write(diagram)

    def generate_deployment_diagram(self) -> None:
        """Generate deployment architecture diagram."""
        diagram = """# Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevMachine[Developer Machine]
        LocalVenv[Virtual Environment]
        LocalFiles[Local File System]
        DevTools[Development Tools<br/>IDE, Git, Testing]
    end

    subgraph "Production Environment"
        ProdServer[Production Server]
        ProdVenv[Production Virtual Environment]

        subgraph "File Storage"
            NewsDir[../News/ Directory]
            CapcatsDir[../Capcats/ Directory]
            LogDir[Log Files]
            ConfigDir[Configuration Files]
        end

        subgraph "Process Management"
            CronJobs[Cron Jobs]
            SystemdService[Systemd Service]
            ProcessMonitor[Process Monitoring]
        end
    end

    subgraph "Docker Environment"
        DockerContainer[Capcat Container]
        VolumeMount[Volume Mounts]
        NetworkConfig[Network Configuration]
        HealthChecks[Health Checks]
    end

    subgraph "CI/CD Pipeline"
        GitRepo[Git Repository]
        GithubActions[GitHub Actions]

        subgraph "Build Pipeline"
            LintCheck[Code Linting]
            UnitTests[Unit Tests]
            IntegrationTests[Integration Tests]
            DocGeneration[Documentation Generation]
            PackageBuilding[Package Building]
        end

        subgraph "Deploy Pipeline"
            Staging[Staging Environment]
            ProductionDeploy[Production Deployment]
            HealthValidation[Health Validation]
            Rollback[Rollback Capability]
        end
    end

    subgraph "External Dependencies"
        NewsSourcesExt[News Sources APIs]
        NetworkExt[Internet Access]
        DNSExt[DNS Resolution]
    end

    %% Development flow
    DevMachine --> LocalVenv
    LocalVenv --> LocalFiles
    DevMachine --> DevTools

    %% Production deployment
    ProdServer --> ProdVenv
    ProdVenv --> NewsDir
    ProdVenv --> CapcatsDir
    ProdVenv --> LogDir
    ProdVenv --> ConfigDir

    ProdServer --> CronJobs
    ProdServer --> SystemdService
    ProdServer --> ProcessMonitor

    %% Docker deployment
    DockerContainer --> VolumeMount
    DockerContainer --> NetworkConfig
    DockerContainer --> HealthChecks
    VolumeMount --> NewsDir
    VolumeMount --> CapcatsDir

    %% CI/CD flow
    GitRepo --> GithubActions
    GithubActions --> LintCheck
    LintCheck --> UnitTests
    UnitTests --> IntegrationTests
    IntegrationTests --> DocGeneration
    DocGeneration --> PackageBuilding

    PackageBuilding --> Staging
    Staging --> ProductionDeploy
    ProductionDeploy --> HealthValidation
    HealthValidation --> Rollback

    %% External dependencies
    ProdVenv --> NewsSourcesExt
    DockerContainer --> NewsSourcesExt
    ProdServer --> NetworkExt
    DockerContainer --> NetworkExt
    NetworkExt --> DNSExt

    %% Styling
    classDef dev fill:#e3f2fd
    classDef prod fill:#e8f5e8
    classDef docker fill:#fff3e0
    classDef cicd fill:#f3e5f5
    classDef external fill:#fce4ec

    class DevMachine,LocalVenv,LocalFiles,DevTools dev
    class ProdServer,ProdVenv,NewsDir,CapcatsDir,LogDir,ConfigDir,CronJobs,SystemdService,ProcessMonitor prod
    class DockerContainer,VolumeMount,NetworkConfig,HealthChecks docker
    class GitRepo,GithubActions,LintCheck,UnitTests,IntegrationTests,DocGeneration,PackageBuilding,Staging,ProductionDeploy,HealthValidation,Rollback cicd
    class NewsSourcesExt,NetworkExt,DNSExt external
```

## Deployment Options

### 1. Direct Installation
```bash
# System-wide installation
sudo pip install capcat
capcat bundle tech --count 10

# User installation
pip install --user capcat
~/.local/bin/capcat bundle tech --count 10
```

### 2. Virtual Environment
```bash
# Development setup
python3 -m venv capcat-env
source capcat-env/bin/activate
pip install -r requirements.txt
./capcat bundle tech --count 10
```

### 3. Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x capcat

VOLUME ["/app/output"]
CMD ["./capcat", "bundle", "tech", "--count", "10"]
```

### 4. Systemd Service
```ini
[Unit]
Description=Capcat News Archiver
After=network.target

[Service]
Type=oneshot
User=capcat
WorkingDirectory=/opt/capcat
ExecStart=/opt/capcat/venv/bin/python capcat.py bundle tech --count 30
Environment=CAPCAT_OUTPUT_DIR=/var/lib/capcat/news

[Install]
WantedBy=multi-user.target
```

### 5. Cron Job
```bash
# Daily news archiving at 6 AM
0 6 * * * /opt/capcat/venv/bin/python /opt/capcat/capcat.py bundle tech --count 30
```

## Security Considerations

- **File Permissions**: Restrict write access to output directories
- **Network Access**: Firewall rules for external connections
- **User Isolation**: Run under dedicated service account
- **Log Security**: Secure log file access and rotation
- **Dependency Management**: Regular security updates
"""

        with open(self.diagrams_dir / "deployment.md", 'w') as f:
            f.write(diagram)

    def generate_class_diagrams(self) -> None:
        """Generate class diagrams for key components."""
        diagram = """# Class Diagrams

## Core Source System Classes

```mermaid
classDiagram
    class BaseSource {
        +name
        +display_name
        +category
        +__init__()
        +get_articles(count)
        +get_article_content(url)
        +validate()
        +get_rate_limit()
        +get_user_agent()
    }

    class ConfigDrivenSource {
        +config
        +selectors
        +__init__(config)
        +get_articles(count)
        +get_article_content(url)
        +validate()
        -_parse_article_list(html)
        -_extract_content(html)
    }

    class CustomSource {
        +__init__()
        +get_articles(count)
        +get_article_content(url)
        +get_comments(url)
        -_custom_processing()
    }

    class HackerNewsSource {
        +api_base
        +__init__()
        +get_articles(count)
        +get_article_content(url)
        +get_comments(url)
        -_fetch_from_api(endpoint)
        -_process_comments(comments)
    }

    class BBCSource {
        +rss_url
        +__init__()
        +get_articles(count)
        +get_article_content(url)
        -_parse_rss(xml)
        -_extract_bbc_content(html)
    }

    class SourceFactory {
        +registry
        +__init__(registry)
        +create_source(name)
        +get_available_sources()
        +validate_source(name)
        -_resolve_source_type(name)
    }

    class SourceRegistry {
        +sources
        +__init__()
        +register_source(metadata)
        +get_source_metadata(name)
        +list_sources()
        +discover_sources()
        -_load_config_driven_sources()
        -_load_custom_sources()
    }

    class Article {
        +title
        +url
        +content
        +author
        +published_date
        +source
        +metadata
        +comments
        +media_urls
    }

    class Comment {
        +author
        +content
        +timestamp
        +replies
        +score
    }

    BaseSource <|-- ConfigDrivenSource
    BaseSource <|-- CustomSource
    CustomSource <|-- HackerNewsSource
    CustomSource <|-- BBCSource
    SourceFactory --> BaseSource  : creates
    SourceFactory --> SourceRegistry  : uses
    SourceRegistry --> BaseSource  : manages
    BaseSource --> Article  : produces
    Article --> Comment  : contains
```

## Media Processing Classes

```mermaid
classDiagram
    class UnifiedMediaProcessor {
        +session
        +output_dir
        +download_media
        +__init__(session, output_dir, download_media)
        +process_article_media(article)
        +download_images(urls)
        +download_media_files(urls)
        -_detect_media_type(url)
        -_organize_media_files()
    }

    class ImageProcessor {
        +max_size
        +quality
        +__init__(max_size, quality)
        +process_image(file_path)
        +resize_image(image)
        +optimize_image(image)
        +convert_format(image)
        -_validate_image(file_path)
    }

    class MediaDownloader {
        +session
        +timeout
        +retry_count
        +__init__(session, timeout, retry_count)
        +download_file(url)
        +get_file_info(url)
        +validate_download(file_path)
        -_create_directories(path)
        -_handle_download_error(error)
    }

    class ContentFormatter {
        +markdown_options
        +__init__(options)
        +html_to_markdown(html)
        +process_images(content)
        +update_links(content)
        +clean_html(html)
        -_convert_tables(html)
        -_handle_code_blocks(html)
    }

    UnifiedMediaProcessor --> ImageProcessor  : uses
    UnifiedMediaProcessor --> MediaDownloader  : uses
    UnifiedMediaProcessor --> ContentFormatter  : uses
    ImageProcessor --> PIL  : uses
    MediaDownloader --> requests  : uses
    ContentFormatter --> BeautifulSoup  : uses
```

## HTML Generation Classes

```mermaid
classDiagram
    class BaseHTMLGenerator {
        +template_dir
        +theme
        +__init__(template_dir, theme)
        +generate_html(article)
        +load_template(name)
        +render_template(template)
        -_prepare_context(article)
        -_copy_assets(output_dir)
    }

    class ArticleHTMLGenerator {
        +source_config
        +__init__(template_dir, theme, source_config)
        +generate_html(article)
        +generate_index(articles)
        -_generate_navigation(articles)
        -_process_article_content(content)
    }

    class CommentHTMLGenerator {
        +comment_template
        +__init__(template_dir, theme)
        +render_comments(comments)
        +render_comment_tree(comment)
        -_anonymize_usernames(comments)
        -_format_timestamps(comments)
    }

    class ThemeManager {
        +themes_dir
        +current_theme
        +__init__(themes_dir, default_theme)
        +load_theme(name)
        +get_css_files(theme)
        +get_js_files(theme)
        +validate_theme(name)
        -_copy_theme_assets(theme)
    }

    BaseHTMLGenerator <|-- ArticleHTMLGenerator
    ArticleHTMLGenerator --> CommentHTMLGenerator  : uses
    BaseHTMLGenerator --> ThemeManager  : uses
    ThemeManager --> Jinja2  : uses
```

## Configuration Classes

```mermaid
classDiagram
    class ConfigManager {
        +config_file
        +config_data
        +__init__(config_file)
        +load_config()
        +get_setting(key)
        +update_setting(key)
        +save_config()
        +validate_config()
        -_merge_configs(base)
        -_expand_environment_variables(config)
    }

    class SourceConfig {
        +name
        +display_name
        +base_url
        +category
        +selectors
        +rate_limit
        +__init__(config_dict)
        +validate()
        +to_dict()
        -_validate_selectors()
        -_validate_urls()
    }

    class CLIConfig {
        +args
        +__init__(args)
        +get_sources()
        +get_output_dir()
        +get_count()
        +should_download_media()
        +should_generate_html()
        +get_log_level()
    }

    ConfigManager --> SourceConfig  : creates
    CLIConfig --> ConfigManager  : uses
```
"""

        with open(self.diagrams_dir / "class_diagrams.md", 'w') as f:
            f.write(diagram)


def main():
    """Main diagram generation function."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "docs")

    print("Generating architecture diagrams...")
    generator = DiagramGenerator(output_dir)
    generator.generate_all_diagrams()

    print(f"Diagrams generated in: {output_dir}/diagrams/")


if __name__ == "__main__":
    main()