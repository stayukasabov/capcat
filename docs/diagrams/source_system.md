# Source System Architecture

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
