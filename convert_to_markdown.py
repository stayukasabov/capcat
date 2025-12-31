#!/usr/bin/env python3
import re
import base64
from html.parser import HTMLParser
from pathlib import Path

class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.current_tag = []
        self.in_content = False
        self.list_level = 0
        self.in_list_item = False
        self.skip_content = False
        self.current_text = ""
        self.images = []
        self.links = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Start capturing content when we hit the main article
        if tag in ['article', 'main'] or attrs_dict.get('class', '') == 'content-title':
            self.in_content = True

        if not self.in_content:
            return

        # Skip script and style tags
        if tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip_content = True
            return

        self.current_tag.append(tag)

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.current_text = '#' * level + ' '
        elif tag == 'p':
            pass
        elif tag == 'strong' or tag == 'b':
            self.current_text += '**'
        elif tag == 'em' or tag == 'i':
            self.current_text += '*'
        elif tag == 'a':
            href = attrs_dict.get('href', attrs_dict.get('data-savepage-href', ''))
            self.links[len(self.markdown)] = href
            self.current_text += '['
        elif tag == 'img':
            src = attrs_dict.get('src', attrs_dict.get('data-savepage-src', ''))
            alt = attrs_dict.get('alt', 'Image')
            self.images.append({'src': src, 'alt': alt})
            self.current_text += f'\n![{alt}](image_{len(self.images)})\n'
        elif tag == 'ul':
            self.list_level += 1
        elif tag == 'ol':
            self.list_level += 1
        elif tag == 'li':
            self.in_list_item = True
            self.current_text += '  ' * (self.list_level - 1) + '- '
        elif tag == 'code':
            self.current_text += '`'
        elif tag == 'pre':
            self.current_text += '\n```\n'
        elif tag == 'br':
            self.current_text += '\n'
        elif tag == 'blockquote':
            self.current_text += '\n> '

    def handle_endtag(self, tag):
        if self.skip_content and tag in ['script', 'style', 'nav', 'header', 'footer']:
            self.skip_content = False
            return

        if not self.in_content or self.skip_content:
            return

        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
            if self.current_text.strip():
                self.markdown.append(self.current_text.strip())
                self.markdown.append('')
            self.current_text = ""
        elif tag == 'strong' or tag == 'b':
            self.current_text += '**'
        elif tag == 'em' or tag == 'i':
            self.current_text += '*'
        elif tag == 'a':
            link_pos = len(self.markdown)
            href = self.links.get(link_pos, '#')
            self.current_text += f']({href})'
        elif tag == 'ul' or tag == 'ol':
            self.list_level -= 1
            if self.list_level == 0:
                self.markdown.append('')
        elif tag == 'li':
            self.in_list_item = False
            if self.current_text.strip():
                self.markdown.append(self.current_text.strip())
            self.current_text = ""
        elif tag == 'code':
            self.current_text += '`'
        elif tag == 'pre':
            self.current_text += '\n```\n'
        elif tag == 'blockquote':
            if self.current_text.strip():
                self.markdown.append(self.current_text.strip())
                self.markdown.append('')
            self.current_text = ""

    def handle_data(self, data):
        if self.in_content and not self.skip_content:
            clean_data = ' '.join(data.split())
            if clean_data:
                self.current_text += clean_data + ' '

    def get_markdown(self):
        # Flush any remaining text
        if self.current_text.strip():
            self.markdown.append(self.current_text.strip())

        # Clean up multiple blank lines
        result = []
        prev_blank = False
        for line in self.markdown:
            if not line.strip():
                if not prev_blank:
                    result.append('')
                    prev_blank = True
            else:
                result.append(line)
                prev_blank = False

        return '\n'.join(result), self.images

def create_mermaid_diagram(image_context, index):
    """Create a mermaid diagram based on image context"""
    context_lower = image_context.lower()

    # Journey map diagram
    if 'journey' in context_lower or 'path' in context_lower or 'user flow' in context_lower:
        return """```mermaid
journey
    title User Journey Map
    section Discovery
      User identifies need: 5: User
      Searches for solution: 4: User
    section Evaluation
      Reviews options: 4: User
      Compares features: 3: User
    section Decision
      Makes selection: 5: User
      Completes action: 5: User
    section Experience
      Uses product: 4: User
      Achieves goal: 5: User
```"""

    # Flowchart diagram
    elif 'flow' in context_lower or 'process' in context_lower or 'step' in context_lower:
        return """```mermaid
flowchart TD
    A[Start] --> B{Decision Point}
    B -->|Option 1| C[Action 1]
    B -->|Option 2| D[Action 2]
    C --> E[Next Step]
    D --> E
    E --> F[End]
```"""

    # Sequence diagram
    elif 'interaction' in context_lower or 'sequence' in context_lower or 'communication' in context_lower:
        return """```mermaid
sequenceDiagram
    participant U as User
    participant S as System
    participant D as Database
    U->>S: Request Action
    S->>D: Query Data
    D-->>S: Return Data
    S-->>U: Display Result
```"""

    # Timeline diagram
    elif 'timeline' in context_lower or 'time' in context_lower or 'phase' in context_lower:
        return """```mermaid
timeline
    title Project Timeline
    section Phase 1
        Research : Discovery
                : Analysis
    section Phase 2
        Design : Wireframes
              : Prototypes
    section Phase 3
        Development : Implementation
                   : Testing
    section Phase 4
        Launch : Deployment
              : Monitoring
```"""

    # Mind map / concept diagram
    elif 'concept' in context_lower or 'mind' in context_lower or 'idea' in context_lower:
        return """```mermaid
mindmap
  root((User Journey))
    Touchpoints
      Website
      Mobile App
      Customer Service
    Emotions
      Satisfaction
      Frustration
      Delight
    Actions
      Browse
      Purchase
      Review
```"""

    # Default: simple diagram
    else:
        return f"""```mermaid
graph LR
    A[User Journey Mapping] --> B[Define Objectives]
    B --> C[Identify Touchpoints]
    C --> D[Map User Actions]
    D --> E[Analyze Pain Points]
    E --> F[Optimize Experience]
```"""

def main():
    input_file = Path("/Users/xpro/SynologyDrive/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/UXJourney/User journey mapping_ guide with tools and examples - Justinmind.html")
    output_file = Path("/Users/xpro/SynologyDrive/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat copy/Application/UXJourney/user_journey_mapping_guide.md")

    print(f"Reading HTML file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Converting HTML to Markdown...")
    converter = HTMLToMarkdownConverter()
    converter.feed(html_content)
    markdown_text, images = converter.get_markdown()

    print(f"Found {len(images)} images to convert to mermaid diagrams")

    # Replace image placeholders with mermaid diagrams
    for i, img in enumerate(images, 1):
        alt_text = img['alt']
        mermaid_diagram = create_mermaid_diagram(alt_text, i)
        markdown_text = markdown_text.replace(f'![{alt_text}](image_{i})',
                                              f'\n### {alt_text}\n\n{mermaid_diagram}\n')

    print(f"Writing markdown file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# The Ultimate Guide to User Journey Mapping: Tools and Examples\n\n")
        f.write(markdown_text)

    print(f"\nConversion complete! Output saved to: {output_file}")
    print(f"- Converted HTML content to Markdown")
    print(f"- Replaced {len(images)} images with contextual Mermaid diagrams")

if __name__ == '__main__':
    main()
