#!/usr/bin/env python3
"""
Static site generator for the RNA-seq workshop markdown files.
Creates a single-page HTML site with navigation.
"""

import os
import re
from pathlib import Path
import markdown
from markdown.extensions import codehilite, tables, fenced_code

# Configuration
SITE_DIR = "docs"
CONTENT_DIR = "."

# Define the book structure
BOOK_STRUCTURE = [
    ("index.md", "Introduction"),
    ("welcome-setup.md", "Welcome and Setup"),
    ("useful_links.md", "Useful Links"),
    ("Day 1", [
        ("Day-1/01-shell-basics.md", "Shell Basics"),
        ("Day-1/02-Data-management-and-setup.md", "Data Management and Setup"),
        ("Day-1/03-FASTQ-files-and-basic-QC.md", "FASTQ Files and Basic QC"),
        ("Day-1/04-challenge_exercises.md", "Challenge Exercises"),
    ]),
    ("Day 2", [
        ("Day-2/01-read-mapping.md", "Read Mapping"),
        ("Day-2/02-alignment-QC.md", "Alignment QC"),
        ("Day-2/03-challenge_exercise.md", "Challenge Exercise"),
    ]),
    ("Day 3", [
        ("Day-3/01-quantification.md", "Quantification"),
        ("Day-3/02-normalization.md", "Normalization"),
        ("Day-3/03-joining-the-workflow.md", "Joining the Workflow"),
        ("Day-3/closing_remarks.md", "Closing Remarks"),
    ]),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RNA-seq Primary Data Analysis Workshop</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }}
        
        .sidebar {{
            width: 280px;
            background: #2c3e50;
            color: white;
            padding: 20px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}
        
        .sidebar h1 {{
            font-size: 1.2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #34495e;
        }}
        
        .sidebar ul {{
            list-style: none;
        }}
        
        .sidebar li {{
            margin: 5px 0;
        }}
        
        .sidebar a {{
            color: #ecf0f1;
            text-decoration: none;
            display: block;
            padding: 8px 12px;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .sidebar a:hover {{
            background: #34495e;
        }}
        
        .sidebar .part-title {{
            color: #95a5a6;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 5px;
            padding: 8px 12px;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        
        .content {{
            flex: 1;
            padding: 40px;
            max-width: 900px;
        }}
        
        .content h1 {{
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .content h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        .content h3 {{
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 12px;
        }}
        
        .content p {{
            margin-bottom: 15px;
        }}
        
        .content img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .content pre {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .content code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .content pre code {{
            background: none;
            padding: 0;
        }}
        
        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .content table th,
        .content table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        .content table th {{
            background: #2c3e50;
            color: white;
        }}
        
        .content table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .content blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            color: #555;
        }}
        
        .content ul, .content ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        .content li {{
            margin: 8px 0;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <h1>RNA-seq Workshop</h1>
            {nav}
        </nav>
        <main class="content">
            {content}
        </main>
    </div>
</body>
</html>
"""

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return None, content

def markdown_to_html(md_content, base_path='.'):
    """Convert markdown to HTML, handling images and links."""
    # Fix markdown image syntax: ![alt](../figures/image.png) -> ![alt](figures/image.png)
    md_content = re.sub(r'!\[([^\]]*)\]\(\.\./figures/([^)]+)\)', 
                       lambda m: f'![{m.group(1)}](figures/{m.group(2)})',
                       md_content)
    # Also handle cases without ../
    md_content = re.sub(r'!\[([^\]]*)\]\(figures/([^)]+)\)', 
                       lambda m: f'![{m.group(1)}](figures/{m.group(2)})',
                       md_content)
    
    # Fix HTML img tags: <img src="../figures/image.png"> -> <img src="figures/image.png">
    md_content = re.sub(r'<img\s+([^>]*?)src=["\']\.\./figures/([^"\']+)["\']([^>]*?)>', 
                       lambda m: f'<img {m.group(1)}src="figures/{m.group(2)}"{m.group(3)}>',
                       md_content, flags=re.IGNORECASE)
    # Also handle cases without ../
    md_content = re.sub(r'<img\s+([^>]*?)src=["\']figures/([^"\']+)["\']([^>]*?)>', 
                       lambda m: f'<img {m.group(1)}src="figures/{m.group(2)}"{m.group(3)}>',
                       md_content, flags=re.IGNORECASE)
    
    # Configure markdown
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables',
        'fenced_code',
        'toc',
        'nl2br',
    ])
    
    html = md.convert(md_content)
    
    # Also fix any remaining image paths in the converted HTML
    html = re.sub(r'src=["\']\.\./figures/([^"\']+)["\']', 
                 lambda m: f'src="figures/{m.group(1)}"',
                 html, flags=re.IGNORECASE)
    
    return html

def build_navigation(structure):
    """Build navigation HTML from book structure."""
    nav_items = []
    top_level_items = []
    
    for item in structure:
        if isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[1], list):
                # It's a part with chapters
                part_title, chapters = item
                nav_items.append(f'<div class="part-title">{part_title}</div>')
                nav_items.append('<ul>')
                for chapter_file, chapter_title in chapters:
                    anchor = chapter_file.replace('/', '-').replace('.md', '')
                    nav_items.append(f'<li><a href="#{anchor}">{chapter_title}</a></li>')
                nav_items.append('</ul>')
            else:
                # It's a single chapter - collect for top-level ul
                chapter_file, chapter_title = item
                anchor = chapter_file.replace('/', '-').replace('.md', '')
                top_level_items.append(f'<li><a href="#{anchor}">{chapter_title}</a></li>')
    
    # Wrap top-level items in ul if there are any
    if top_level_items:
        return '<ul>\n' + '\n'.join(top_level_items) + '\n</ul>\n' + '\n'.join(nav_items)
    else:
        return '\n'.join(nav_items)

def build_content(structure, base_path='.'):
    """Build main content HTML from book structure."""
    content_sections = []
    
    for item in structure:
        if isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[1], list):
                # It's a part with chapters
                part_title, chapters = item
                content_sections.append(f'<h1>{part_title}</h1>')
                for chapter_file, chapter_title in chapters:
                    file_path = os.path.join(base_path, chapter_file)
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            md_content = f.read()
                        
                        _, content = extract_frontmatter(md_content)
                        anchor = chapter_file.replace('/', '-').replace('.md', '')
                        html_content = markdown_to_html(content, base_path)
                        content_sections.append(f'<section id="{anchor}">')
                        content_sections.append(f'<h2>{chapter_title}</h2>')
                        content_sections.append(html_content)
                        content_sections.append('</section>')
            else:
                # It's a single chapter
                chapter_file, chapter_title = item
                file_path = os.path.join(base_path, chapter_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    
                    _, content = extract_frontmatter(md_content)
                    anchor = chapter_file.replace('/', '-').replace('.md', '')
                    html_content = markdown_to_html(content, base_path)
                    content_sections.append(f'<section id="{anchor}">')
                    content_sections.append(f'<h1>{chapter_title}</h1>')
                    content_sections.append(html_content)
                    content_sections.append('</section>')
    
    return '\n'.join(content_sections)

def main():
    """Main function to build the site."""
    # Create output directory
    os.makedirs(SITE_DIR, exist_ok=True)
    
    # Build navigation and content
    nav = build_navigation(BOOK_STRUCTURE)
    content = build_content(BOOK_STRUCTURE, CONTENT_DIR)
    
    # Generate HTML
    html = HTML_TEMPLATE.format(nav=nav, content=content)
    
    # Write index.html
    output_path = os.path.join(SITE_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Copy figures directory if it exists
    figures_src = os.path.join(CONTENT_DIR, 'figures')
    figures_dst = os.path.join(SITE_DIR, 'figures')
    if os.path.exists(figures_src):
        import shutil
        if os.path.exists(figures_dst):
            shutil.rmtree(figures_dst)
        shutil.copytree(figures_src, figures_dst)
    
    # Create .nojekyll file for GitHub Pages (prevents Jekyll processing)
    nojekyll_path = os.path.join(SITE_DIR, '.nojekyll')
    with open(nojekyll_path, 'w') as f:
        f.write('')
    
    print(f"Site built successfully! Open {output_path} in your browser.")
    print(f"\nFor GitHub Pages:")
    print(f"1. Push the {SITE_DIR}/ directory to the 'gh-pages' branch, OR")
    print(f"2. Configure GitHub Pages to use the '{SITE_DIR}/' directory as the source")

if __name__ == '__main__':
    main()

