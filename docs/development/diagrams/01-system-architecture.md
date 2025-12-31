# System Architecture Diagrams

## Complete System Architecture

```mermaid
graph TB
    subgraph User Interface Layer
        CLI[CLI Interface<br/>cli.py]
        Interactive[Interactive Mode<br/>interactive.py]
        Wrapper[Bash Wrapper<br/>capcat]
    end

    subgraph Core Orchestration Layer
        Main[Main Application<br/>capcat.py]
        Config[Configuration<br/>config.py]
        Logging[Logging System<br/>logging_config.py]
        Shutdown[Graceful Shutdown<br/>shutdown.py]
    end

    subgraph Source System Layer
        Registry[Source Registry<br/>Discovery & Management]
        Factory[Source Factory<br/>Instantiation]
        Monitor[Performance Monitor<br/>Metrics & Health]
    end

    subgraph Hybrid Source Implementation
        ConfigDriven[Config-Driven Sources<br/>YAML-based]
        Custom[Custom Sources<br/>Python classes]
        BaseSource[Base Source<br/>Abstract interface]
    end

    subgraph Shared Infrastructure
        SessionPool[Session Pool<br/>Connection reuse]
        ArticleFetcher[Article Fetcher<br/>Content processing]
        MediaProcessor[Media Processor<br/>Image/video handling]
        HTMLConverter[HTML Converter<br/>Markdown generation]
    end

    subgraph Output Layer
        FileWriter[File Writer<br/>Markdown output]
        HTMLGen[HTML Generator<br/>Web view]
        MediaDownload[Media Downloader<br/>File management]
    end

    CLI --> Main
    Interactive --> Main
    Wrapper --> CLI

    Main --> Config
    Main --> Logging
    Main --> Shutdown
    Main --> Registry

    Registry --> Factory
    Registry --> Monitor
    Factory --> ConfigDriven
    Factory --> Custom

    ConfigDriven --> BaseSource
    Custom --> BaseSource

    BaseSource --> SessionPool
    BaseSource --> ArticleFetcher
    ArticleFetcher --> MediaProcessor
    ArticleFetcher --> HTMLConverter

    HTMLConverter --> FileWriter
    FileWriter --> HTMLGen
    MediaProcessor --> MediaDownload

    style Main fill:#d75f00,stroke:#333,stroke-width:4px,color:#fff
    style Registry fill:#4ecdc4,stroke:#333,stroke-width:2px
    style Factory fill:#4ecdc4,stroke:#333,stroke-width:2px
```

## Data Flow Architecture

```mermaid
flowchart TD
    User[User Command] --> Parse[CLI Parser]
    Parse --> Validate[Input Validation]
    Validate --> Registry[Source Registry]

    Registry --> Discover[Discover Sources]
    Discover --> ConfigSources[Config YAML Files]
    Discover --> CustomSources[Custom Python Classes]

    ConfigSources --> Factory
    CustomSources --> Factory

    Factory[Source Factory] --> Instantiate[Create Source Instances]
    Instantiate --> Pool[Shared Session Pool]

    Pool --> Parallel[Parallel Execution]

    Parallel --> S1[Source 1<br/>get_articles]
    Parallel --> S2[Source 2<br/>get_articles]
    Parallel --> S3[Source N<br/>get_articles]

    S1 --> Articles1[Articles List]
    S2 --> Articles2[Articles List]
    S3 --> Articles3[Articles List]

    Articles1 --> Process[Processing Pipeline]
    Articles2 --> Process
    Articles3 --> Process

    Process --> Fetch[Fetch Content]
    Fetch --> Extract[Extract Text]
    Extract --> Media[Process Media]
    Media --> Convert[Convert to Markdown]

    Convert --> Output[Output Generation]
    Output --> Structure[Create Folder Structure]
    Structure --> Write[Write Files]
    Write --> Generate[Generate HTML Optional]

    Generate --> Complete[Operation Complete]
    Complete --> Report[Display Summary]

    style Parse fill:#ffa500,stroke:#333,stroke-width:2px
    style Factory fill:#4ecdc4,stroke:#333,stroke-width:2px
    style Parallel fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
    style Process fill:#4ecdc4,stroke:#333,stroke-width:2px
```

## Hybrid Source System

```mermaid
graph LR
    subgraph Source Discovery
        A[sources/active/] --> B[config_driven/]
        A --> C[custom/]
    end

    B --> B1[configs/*.yaml]
    C --> C1[*/source.py]

    B1 --> D[Config-Driven Source]
    C1 --> E[Custom Source]

    D --> F[Base Source Interface]
    E --> F

    F --> G{get_articles method}

    G --> H[Returns Article objects]

    D --> D1[Simple Setup<br/>15-30 min]
    D --> D2[YAML configuration]
    D --> D3[BeautifulSoup]
    D --> D4[No Python coding]

    E --> E1[Complex Setup<br/>2-4 hours]
    E --> E2[Full Python control]
    E --> E3[API integration]
    E --> E4[Comment systems]

    style D fill:#4ecdc4,stroke:#333,stroke-width:2px
    style E fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#ffa500,stroke:#333,stroke-width:2px
```

## Design Patterns Applied

```mermaid
mindmap
  root((Design<br/>Patterns))
    Factory Pattern
      Source creation
      Unified interface
      Type abstraction
      Instance management
    Registry Pattern
      Auto-discovery
      Source catalog
      Validation
      Lookup service
    Strategy Pattern
      Content extraction
      Multiple algorithms
      Pluggable extractors
      Fallback options
    Observer Pattern
      Progress tracking
      Event notification
      UI updates
      Logging hooks
    Session Pooling
      Connection reuse
      Performance boost
      Resource sharing
      HTTP optimization
    Singleton
      Registry instance
      Config manager
      Session pool
      Logger
```

## Processing Pipeline Detailed

```mermaid
sequenceDiagram
    participant U as User
    participant M as Main App
    participant R as Registry
    participant F as Factory
    participant S as Source
    participant A as Article Fetcher
    participant MP as Media Processor
    participant FW as File Writer

    U->>M: ./capcat fetch hn --count 10
    M->>R: get_source('hn')
    R->>R: Lookup source config
    R->>F: create_source(config)
    F->>S: new HackerNewsSource(config, session)
    F-->>M: Source instance

    M->>S: get_articles(count=10)
    activate S
    S->>S: Fetch article URLs
    S->>S: For each article:
    S->>A: fetch_content(url)
    activate A
    A->>A: HTTP request
    A->>A: Parse HTML
    A->>A: Extract content
    A-->>S: Article content
    deactivate A

    S->>S: Fetch comments (if applicable)
    S-->>M: List of 10 Articles
    deactivate S

    M->>M: For each article:
    M->>MP: process_media(article)
    activate MP
    MP->>MP: Find image URLs
    MP->>MP: Download images
    MP->>MP: Convert to local paths
    MP-->>M: Updated article
    deactivate MP

    M->>FW: write_article(article, path)
    activate FW
    FW->>FW: Create folder structure
    FW->>FW: Write article.md
    FW->>FW: Copy media files
    FW-->>M: Success
    deactivate FW

    M-->>U: [OK] 10 articles saved
```

## Error Handling Hierarchy

```mermaid
graph TD
    A[CapcatError<br/>Base Exception] --> B[ConfigurationError]
    A --> C[SourceError]
    A --> D[NetworkError]
    A --> E[ProcessingError]
    A --> F[FileSystemError]

    B --> B1[InvalidConfigError]
    B --> B2[MissingConfigError]

    C --> C1[SourceNotFoundError]
    C --> C2[SourceUnavailableError]
    C --> C3[ArticleFetchError]

    D --> D1[ConnectionError]
    D --> D2[TimeoutError]
    D --> D3[DNSError]

    E --> E1[ParseError]
    E --> E2[ConversionError]
    E --> E3[MediaDownloadError]

    F --> F1[PermissionError]
    F --> F2[DiskFullError]
    F --> F3[PathError]

    style A fill:#d75f00,stroke:#333,stroke-width:3px,color:#fff
    style B fill:#ffa500,stroke:#333,stroke-width:2px
    style C fill:#ffa500,stroke:#333,stroke-width:2px
    style D fill:#ffa500,stroke:#333,stroke-width:2px
    style E fill:#ffa500,stroke:#333,stroke-width:2px
    style F fill:#ffa500,stroke:#333,stroke-width:2px
```

## Performance Optimization Strategy

```mermaid
graph TB
    subgraph Optimization Techniques
        A1[Parallel Processing]
        A2[Connection Pooling]
        A3[Lazy Loading]
        A4[Caching]
    end

    A1 --> B1[ThreadPoolExecutor]
    A1 --> B2[Concurrent article fetching]
    A1 --> B3[5x faster than sequential]

    A2 --> C1[requests.Session reuse]
    A2 --> C2[HTTP keep-alive]
    A2 --> C3[70% time reduction]

    A3 --> D1[Content on demand]
    A3 --> D2[Comments when needed]
    A3 --> D3[Memory efficient]

    A4 --> E1[Config file caching]
    A4 --> E2[@lru_cache decorator]
    A4 --> E3[Avoid redundant I/O]

    B1 --> F[Performance Gains]
    C1 --> F
    D1 --> F
    E1 --> F

    F --> G[50-70% Faster<br/>Overall]

    style F fill:#4ecdc4,stroke:#333,stroke-width:2px
    style G fill:#d75f00,stroke:#333,stroke-width:4px,color:#fff
```

## Module Dependencies

```mermaid
graph TD
    subgraph External Dependencies
        E1[requests<br/>HTTP client]
        E2[BeautifulSoup<br/>HTML parsing]
        E3[markdownify<br/>HTML→Markdown]
        E4[questionary<br/>Interactive UI]
        E5[PyYAML<br/>Config parsing]
    end

    subgraph Core Modules
        C1[capcat.py<br/>Main app]
        C2[cli.py<br/>CLI interface]
        C3[interactive.py<br/>Interactive mode]
    end

    subgraph Source System
        S1[source_registry.py]
        S2[source_factory.py]
        S3[base_source.py]
        S4[config_driven_source.py]
    end

    subgraph Processing
        P1[article_fetcher.py]
        P2[unified_media_processor.py]
        P3[html_converter.py]
    end

    E1 --> P1
    E2 --> P1
    E2 --> S4
    E3 --> P3
    E4 --> C3
    E5 --> S1

    C1 --> C2
    C1 --> C3
    C1 --> S1

    S1 --> S2
    S2 --> S3
    S2 --> S4

    S3 --> P1
    P1 --> P2
    P1 --> P3

    style C1 fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
```

## Configuration System

```mermaid
graph LR
    subgraph Priority Levels
        A[Command Line Args<br/>Highest Priority]
        B[Environment Variables]
        C[Config File<br/>capcat.yml]
        D[Default Values<br/>Lowest Priority]
    end

    A --> E{Merge Configuration}
    B --> E
    C --> E
    D --> E

    E --> F[Final Config Object]

    F --> G[Used by Application]

    G --> G1[count: 30]
    G --> G2[output_dir: ../News/]
    G --> G3[media: false]
    G --> G4[html: false]

    style A fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#4ecdc4,stroke:#333,stroke-width:2px
```

## Security Architecture

```mermaid
graph TD
    subgraph Input Layer
        A1[User Input]
        A2[CLI Arguments]
        A3[Config Files]
    end

    A1 --> B[Validation Layer]
    A2 --> B
    A3 --> B

    B --> B1[Type Validation]
    B --> B2[Range Checking]
    B --> B3[Path Sanitization]
    B --> B4[URL Validation]

    B1 --> C{Valid?}
    B2 --> C
    B3 --> C
    B4 --> C

    C -->|No| D[Reject with Error]
    C -->|Yes| E[Processing Layer]

    E --> E1[Content Fetching]
    E --> E2[Media Download]
    E --> E3[File Writing]

    E1 --> F[Privacy Layer]
    E2 --> F
    E3 --> F

    F --> F1[Username Anonymization]
    F --> F2[No Telemetry]
    F --> F3[Local-only Storage]

    F1 --> G[Safe Output]
    F2 --> G
    F3 --> G

    style B fill:#ffa500,stroke:#333,stroke-width:2px
    style F fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#4ecdc4,stroke:#333,stroke-width:2px
```

## Component Communication

```mermaid
graph TB
    subgraph Component A - CLI
        A1[Parse Arguments]
        A2[Validate Input]
        A3[Route Command]
    end

    subgraph Component B - Registry
        B1[Discover Sources]
        B2[Validate Configs]
        B3[Provide Instances]
    end

    subgraph Component C - Factory
        C1[Create Source]
        C2[Inject Dependencies]
        C3[Return Instance]
    end

    subgraph Component D - Source
        D1[Fetch Articles]
        D2[Extract Content]
        D3[Return Data]
    end

    subgraph Component E - Output
        E1[Generate Structure]
        E2[Write Files]
        E3[Report Success]
    end

    A3 -->|source_id| B3
    B3 -->|config| C1
    C1 -->|session| C2
    C2 -->|source| D1
    D1 -->|articles| E1
    E1 -->|paths| E2
    E2 -->|summary| E3
    E3 -->|result| A1

    style A1 fill:#ffa500,stroke:#333,stroke-width:2px
    style B3 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style C2 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style D1 fill:#d75f00,stroke:#333,stroke-width:2px,color:#fff
```

## Scalability Architecture

```mermaid
graph LR
    subgraph Current Scale
        A1[17 Sources]
        A2[100s Articles/batch]
        A3[Single Machine]
    end

    subgraph Optimization Points
        B1[Parallel Processing<br/>ThreadPool]
        B2[Connection Reuse<br/>Session Pool]
        B3[Efficient I/O<br/>Bulk writes]
    end

    subgraph Future Scale Options
        C1[50+ Sources]
        C2[1000s Articles/batch]
        C3[Distributed Processing]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3

    B1 --> C1
    B2 --> C2
    B3 --> C3

    C1 --> D[Horizontal Scaling]
    C2 --> D
    C3 --> D

    D --> E1[Multi-machine]
    D --> E2[Queue-based]
    D --> E3[Cloud deployment]

    style B1 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style B2 fill:#4ecdc4,stroke:#333,stroke-width:2px
    style D fill:#ffa500,stroke:#333,stroke-width:2px
```

## Architecture Evolution

```mermaid
timeline
    title Architecture Evolution
    2020-2021 : Initial Architecture
              : Single source support
              : Synchronous processing
              : No abstraction
    2021-2022 : Multi-source Architecture
              : Multiple sources added
              : Parallel processing
              : Basic source interface
    2022-2023 : Registry Pattern
              : Auto-discovery
              : Dynamic loading
              : Validation system
    2023-2024 : Hybrid Architecture
              : Config-driven sources
              : Custom sources
              : Factory pattern
    2024-2025 : Current Architecture
              : Performance monitor
              : Advanced error handling
              : Enterprise features
```

## Technology Stack

```mermaid
graph TB
    subgraph Core Technologies
        A1[Python 3.8+]
        A2[Standard Library]
    end

    subgraph HTTP & Networking
        B1[requests]
        B2[urllib3]
    end

    subgraph HTML & Content
        C1[BeautifulSoup4]
        C2[lxml]
        C3[markdownify]
    end

    subgraph CLI & UI
        D1[argparse]
        D2[questionary]
        D3[prompt_toolkit]
    end

    subgraph Configuration
        E1[PyYAML]
        E2[python-dotenv]
    end

    subgraph Testing
        F1[pytest]
        F2[pytest-cov]
        F3[pytest-mock]
    end

    A1 --> A2
    A2 --> B1
    B1 --> C1
    C1 --> D1
    D1 --> E1

    style A1 fill:#d75f00,stroke:#333,stroke-width:3px,color:#fff
```
