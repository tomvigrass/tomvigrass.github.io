#!/usr/bin/env python3
"""
CV Generator Script
Converts cv-data.md to HTML with predefined styling
"""

import re
from pathlib import Path
from typing import Dict

def parse_cv_markdown(content: str) -> Dict:
    """Parse the markdown CV data into structured data"""
    sections = {}
    current_section = None
    current_subsection = None
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip title
        if line.startswith('# CV Data'):
            i += 1
            continue
            
        # Main sections
        if line.startswith('## '):
            current_section = line[3:]
            sections[current_section] = {}
            if current_section == 'Personal Information':
                # Parse personal info as key-value pairs
                i += 1
                while i < len(lines) and lines[i].strip():
                    info_line = lines[i].strip()
                    if info_line.startswith('- **'):
                        match = re.match(r'- \*\*(.+?)\*\*: (.+)', info_line)
                        if match:
                            key, value = match.groups()
                            sections[current_section][key] = value
                    i += 1
                continue
            elif current_section in ['Experience', 'Education']:
                sections[current_section]['entries'] = []
        
        # Subsections (### for job roles/education entries)
        elif line.startswith('### '):
            if current_section in ['Experience', 'Education']:
                # Parse job/education entry
                title_parts = line[4:].split(' | ')
                company = title_parts[0]
                role = title_parts[1] if len(title_parts) > 1 else ""
                
                entry = {
                    'company': company,
                    'role': role,
                    'duration': '',
                    'location': '',
                    'description': '',
                    'achievements': []
                }
                
                # Look ahead for duration/location line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('**Duration**'):
                        duration_match = re.search(r'\*\*Duration\*\*: (.+)', next_line)
                        if duration_match:
                            entry['duration'] = duration_match.group(1)
                        i += 1
                        
                        # Check for location
                        if i + 1 < len(lines):
                            loc_line = lines[i + 1].strip()
                            if loc_line.startswith('**Location**'):
                                loc_match = re.search(r'\*\*Location\*\*: (.+)', loc_line)
                                if loc_match:
                                    entry['location'] = loc_match.group(1)
                                i += 1
                
                # Parse description and achievements
                i += 1
                while i < len(lines):
                    desc_line = lines[i].strip()
                    if not desc_line:
                        i += 1
                        continue
                    if desc_line.startswith('### ') or desc_line.startswith('## '):
                        i -= 1
                        break
                    if desc_line.startswith('**Notable projects') or desc_line.startswith('**Projects**'):
                        # Skip the header, achievements follow
                        i += 1
                        continue
                    if desc_line.startswith('- **'):
                        entry['achievements'].append(desc_line[2:])
                    elif not desc_line.startswith('**') and not entry['description']:
                        entry['description'] = desc_line
                    i += 1
                
                sections[current_section]['entries'].append(entry)
                continue
            
        # Handle other subsections
        elif line.startswith('### '):
            current_subsection = line[4:]
            if current_subsection not in sections[current_section]:
                sections[current_section][current_subsection] = []
        
        # Parse content based on current section
        elif line.startswith('- ') and current_section:
            if current_subsection:
                sections[current_section][current_subsection].append(line[2:])
            elif current_section == 'Overview':
                if 'lists' not in sections[current_section]:
                    sections[current_section]['lists'] = {}
                # Look for the preceding header
                prev_line_idx = i - 1
                while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
                    prev_line_idx -= 1
                if prev_line_idx >= 0:
                    prev_line = lines[prev_line_idx].strip()
                    if prev_line.startswith('### '):
                        list_name = prev_line[4:]
                        if list_name not in sections[current_section]['lists']:
                            sections[current_section]['lists'][list_name] = []
                        sections[current_section]['lists'][list_name].append(line[2:])
                        # Continue collecting items for this list
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j].strip()
                            if not next_line or not next_line.startswith('- '):
                                break
                            sections[current_section]['lists'][list_name].append(next_line[2:])
                            j += 1
                        i = j - 1  # Adjust i to account for consumed lines
        
        elif line and not line.startswith('#') and not line.startswith('**') and current_section == 'Overview':
            if 'description' not in sections[current_section]:
                sections[current_section]['description'] = line
        
        i += 1
    
    return sections

def generate_html(data: Dict) -> str:
    """Generate HTML from parsed CV data"""
    
    # CSS styles (copied from original)
    css = """
  @import url(https://themes.googleusercontent.com/fonts/css?kit=xTOoZr6X-i3kNg7pYrzMsnEzyYBuwf3lO_Sc3Mw9RUVbV0WvE1cEyAoIq5yYZlSc);
  body { background:#fff; margin:0; font-family:"Lato", Arial, sans-serif; color:#000;}
  .doc-content { max-width: 820px; padding:36pt 54pt; margin:0 auto;}
  h1 { font-family:"Raleway"; font-weight:700; font-size:12pt; margin:0 0 4pt 0;}
  h2 { font-family:"Lato"; font-weight:700; font-size:11pt; margin:0 0 4pt 0;}
  h3 { font-family:"Lato"; font-weight:400; font-size:9pt; color:#666; margin:0 0 6pt 0;}
  .title { font-family:"Raleway"; font-weight:700; font-size:24pt; line-height:1.0; margin:0;}
  .subtitle { font-family:"Raleway"; font-weight:700; font-size:16pt; color:#f2511b; margin:3pt 0 0 0;}
  .section { margin-top:18pt; }
  .muted { color:#666; }
  .accent { color:#f2511b; }
  ul { margin: 6pt 0 0 18pt; padding:0; }
  li { margin: 3pt 0; }
  .two-col { display:grid; grid-template-columns: 1fr 260px; gap:24px; align-items:start; }
  .small { font-size:10pt; }
  .contact p { margin:0 0 4pt 0; }
  .hr { height:1px; background:#000; opacity:.1; margin:14pt 0; }
  .role { margin-bottom:14pt; }
  .role h2 { font-size:12pt; font-family:"Raleway"; }
  .pill { display:inline-block; border:1px solid rgba(0,0,0,.18); border-radius:12px; padding:3px 8px; margin:3px 6px 0 0; font-size:10pt;}
  .contact a { color:inherit; text-decoration:none; }
  .contact a:hover { text-decoration:underline; }
    """
    
    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '  <meta charset="utf-8">',
        f'  <title>{data["Personal Information"]["Name"]} — CV</title>',
        '  <meta content="text/html; charset=UTF-8" http-equiv="content-type">',
        f'  <style type="text/css">{css}</style>',
        '</head>',
        '<body>',
        '  <div class="doc-content">'
    ]
    
    # Header section
    personal = data.get('Personal Information', {})
    html_parts.extend([
        '    <div class="two-col">',
        '      <div>',
        f'        <div class="title">{personal.get("Name", "")}</div>',
        f'        <div class="subtitle">{personal.get("Title", "")}</div>',
        '      </div>',
        '      <div class="contact small">',
        f'        <p><span class="accent"><a href="mailto:{personal.get("Email", "")}">{personal.get("Email", "")}</a></span></p>',
        f'        <p><span class="accent"><a href="{personal.get("GitHub", "")}">{personal.get("GitHub", "")}</a></span></p>' if personal.get("GitHub") else '',
        '      </div>',
        '    </div>'
    ])
    
    # Overview section
    if 'Overview' in data:
        overview = data['Overview']
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Overview</h1>',
            f'      <p class="small">{overview.get("description", "")}</p>'
        ])
        
        # Add subsections from overview
        if 'lists' in overview:
            for list_name, items in overview['lists'].items():
                html_parts.extend([
                    '',
                    f'      <h2 class="muted">{list_name}</h2>',
                    '      <ul class="small">'
                ])
                for item in items:
                    # Convert markdown bold to HTML
                    item_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
                    html_parts.append(f'        <li>{item_html}</li>')
                html_parts.append('      </ul>')
                html_parts.append('')
                html_parts.append('      <div class="hr"></div>')
        
        # Add technology pills - remove duplicate section
        tech_items = overview.get('lists', {}).get('Key Technology Proficiencies', [])
        if tech_items:
            # Remove the duplicate list version first
            if any('Key Technology Proficiencies' in str(part) for part in html_parts[-10:]):
                # Find and remove the list version
                for i in range(len(html_parts) - 1, max(0, len(html_parts) - 15), -1):
                    if 'Key Technology Proficiencies' in str(html_parts[i]):
                        # Remove from this point until next hr or end
                        j = i
                        while j < len(html_parts) and '<div class="hr"></div>' not in html_parts[j]:
                            j += 1
                        if j < len(html_parts):
                            j += 1  # Include the hr
                        html_parts = html_parts[:i] + html_parts[j:]
                        break
            
            html_parts.extend([
                '      <h2 class="muted">Key technology proficiencies</h2>',
                '      <div class="small">'
            ])
            for tech in tech_items:
                html_parts.append(f'        <span class="pill">{tech}</span>')
            html_parts.append('      </div>')
        
        html_parts.append('    </div>')
    
    # Experience section
    if 'Experience' in data and 'entries' in data['Experience']:
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Experience</h1>'
        ])
        
        for entry in data['Experience']['entries']:
            html_parts.extend([
                '',
                '      <div class="role">',
                f'        <h2>{entry["company"]} / <span class="muted">{entry["role"]}</span></h2>',
                f'        <h3>{entry["duration"]}{", " + entry["location"] if entry["location"] else ""}</h3>',
                f'        <p class="small">{entry["description"]}</p>'
            ])
            
            if entry['achievements']:
                html_parts.extend([
                    '        <h2 class="muted">Notable projects / achievements</h2>',
                    '        <ul class="small">'
                ])
                for achievement in entry['achievements']:
                    # Convert markdown bold to HTML
                    achievement_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', achievement)
                    html_parts.append(f'          <li>{achievement_html}</li>')
                html_parts.append('        </ul>')
            
            html_parts.append('      </div>')
        
        html_parts.append('    </div>')
    
    # Education section
    if 'Education' in data and 'entries' in data['Education']:
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Education</h1>'
        ])
        
        for entry in data['Education']['entries']:
            html_parts.extend([
                '      <div class="role">',
                f'        <h2>{entry["company"]} / <span class="muted">{entry["role"]}</span></h2>',
                f'        <h3>{entry["duration"]}{", " + entry["location"] if entry["location"] else ""}</h3>',
                f'        <p class="small">{entry["description"]}</p>',
                '      </div>'
            ])
        
        html_parts.append('    </div>')
    
    # Close HTML
    html_parts.extend([
        '  </div>',
        '</body>',
        '</html>'
    ])
    
    return '\n'.join(html_parts)

def main():
    """Main function to generate CV HTML from markdown"""
    cv_data_path = Path('cv-data.md')
    output_path = Path('index.html')
    
    if not cv_data_path.exists():
        print(f"Error: {cv_data_path} not found")
        return
    
    # Read and parse markdown
    with open(cv_data_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = parse_cv_markdown(content)
    
    # Generate HTML
    html = generate_html(data)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated {output_path} from {cv_data_path}")

if __name__ == '__main__':
    main()