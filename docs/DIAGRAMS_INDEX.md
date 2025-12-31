# Capcat Visual Documentation Index

## Overview

This index catalogs all Mermaid diagrams in Capcat's documentation. All diagrams are rendered using Mermaid syntax and can be viewed in any Markdown viewer that supports Mermaid.

---

## System Architecture Diagrams

Location: `docs/diagrams/`

### 1. [System Architecture](diagrams/system_architecture.html)
High-level system overview showing the main components and their interactions.

### 2. [Class Diagrams](diagrams/class_diagrams.html)
Core class relationships including:
- Source System Classes (BaseSource, ConfigDrivenSource, CustomSource)
- Media Processing Classes (UnifiedMediaProcessor, ImageProcessor)
- HTML Generation Classes (BaseHTMLGenerator, ArticleHTMLGenerator)
- Configuration Classes (ConfigManager, SourceConfig)

### 3. [Data Flow](diagrams/data_flow.html)
Article processing data flow from user input to final output.

### 4. [Processing Pipeline](diagrams/processing_pipeline.html)
Detailed media and content processing workflow.

### 5. [Source System](diagrams/source_system.html)
Source discovery, registration, and management architecture.

### 6. [Deployment](diagrams/deployment.html)
Deployment architecture and infrastructure setup.

---

## Development Diagrams

Location: `docs/development/diagrams/`

### 1. [System Architecture Deep Dive](development/diagrams/01-system-architecture.html)

Comprehensive architecture analysis including:

**Diagrams Included** (14 diagrams):
1. **Complete System Architecture** - All 5 layers with components
2. **Data Flow Architecture** - End-to-end article fetching flow
3. **Hybrid Source System** - Config-driven vs Custom sources
4. **Design Patterns Mind Map** - Factory, Registry, Strategy, Observer, Singleton
5. **Processing Pipeline Sequence** - Detailed component interactions
6. **Error Handling Hierarchy** - Complete exception tree
7. **Performance Optimization Strategy** - 4 optimization techniques
8. **Module Dependencies** - External and internal dependencies
9. **Configuration System** - Priority levels and merge logic
10. **Security Architecture** - Input validation to safe output
11. **Component Communication** - Inter-component data flow
12. **Scalability Architecture** - Current and future scale
13. **Architecture Evolution Timeline** - 2020-2025 progression
14. **Technology Stack** - Complete tech stack visualization

**Key Insights**:
- 5-layer architecture (UI, Orchestration, Source, Processing, Output)
- Hybrid source system (config-driven + custom)
- 50-70% performance improvement through optimization
- 17 sources currently supported

---

## Diagram Statistics

**Total Diagram Documents**: 7
**Total Individual Diagrams**: 20

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Category</th>
      <th>Documents</th>
      <th>Diagrams</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>System Architecture</td>
      <td>6</td>
      <td>6</td>
    </tr>
    <tr>
      <td>Development Deep Dive</td>
      <td>1</td>
      <td>14</td>
    </tr>
  </tbody>
</table>
</div>

---

## Diagram Types Used

### Flow Charts
**Best For**: Processes, decision trees, workflows
**Syntax**: `flowchart TD` or `graph TD`

### Sequence Diagrams
**Best For**: Component interactions, time-based flows
**Syntax**: `sequenceDiagram`

### Class Diagrams
**Best For**: Object-oriented relationships
**Syntax**: `classDiagram`

### Mind Maps
**Best For**: Exploring relationships, hierarchical concepts
**Syntax**: `mindmap`

### State Diagrams
**Best For**: State transitions, workflow states
**Syntax**: `stateDiagram-v2`

### Timeline Diagrams
**Best For**: Historical progression, stages over time
**Syntax**: `timeline`

### Gantt Charts
**Best For**: Time comparisons, project timelines
**Syntax**: `gantt`

---

## Tools and Resources

### Mermaid Resources

- **Official Docs**: https://mermaid.js.org/
- **Live Editor**: https://mermaid.live/
- **VS Code Extension**: Markdown Preview Mermaid Support
- **GitHub Support**: Native Mermaid rendering

### How to Use These Diagrams

1. **GitHub/GitLab**: Diagrams render automatically in Markdown viewers
2. **VS Code**: Install Mermaid extension for preview
3. **Export**: Use Mermaid Live Editor to export as PNG/SVG
4. **Documentation**: Embed diagram blocks directly in Markdown

---

## Updating Diagrams

### When to Update

1. **Architecture Changes**: Update system diagrams
2. **New Features**: Update user journey diagrams
3. **Process Changes**: Update onboarding diagrams
4. **Metrics Changes**: Update dashboard diagrams

### How to Update

1. Edit source `.md` file in diagrams folder
2. Modify Mermaid code block
3. Test rendering in VS Code or Mermaid Live Editor
4. Commit changes with descriptive message
5. Regenerate HTML: `python3 convert_docs_to_html.py`

---

**Last Updated**: 2025-11-26
**Total Diagrams**: 7 documents containing 20 diagrams
**Maintained By**: Development Team
