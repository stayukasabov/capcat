# System Architecture

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
