# Data Flow Diagram

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
