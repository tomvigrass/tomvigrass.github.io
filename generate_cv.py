#!/usr/bin/env python3
"""
CV Generator Script
Converts JSON Resume format to HTML with predefined styling
"""

import json
import re
from pathlib import Path
from typing import Dict

def load_resume_data(file_path: Path) -> Dict:
    """Load and parse JSON Resume data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date_range(start_date: str, end_date: str = None) -> str:
    """Format date range from JSON Resume format to display format"""
    def format_date(date_str: str) -> str:
        if date_str.lower() == 'present':
            return 'PRESENT'
        # Handle YYYY-MM format
        if len(date_str) == 7 and '-' in date_str:
            year, month = date_str.split('-')
            month_abbrevs = {
                '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
            }
            return f"{month_abbrevs.get(month, month.upper())} {year}"
        return date_str.upper()
    
    start_formatted = format_date(start_date)
    end_formatted = format_date(end_date) if end_date else 'PRESENT'
    
    return f"{start_formatted} – {end_formatted}"

def calculate_duration(start_date: str, end_date: str = None) -> str:
    """Calculate duration between dates"""
    from datetime import datetime
    
    # Parse start date
    start_parts = start_date.split('-')
    start_year = int(start_parts[0])
    start_month = int(start_parts[1]) if len(start_parts) > 1 else 1
    
    # Determine end date
    if end_date and end_date.lower() != 'present':
        end_parts = end_date.split('-')
        end_year = int(end_parts[0])
        end_month = int(end_parts[1]) if len(end_parts) > 1 else 12
    else:
        # Use current date
        now = datetime.now()
        end_year = now.year
        end_month = now.month
    
    # Calculate total months
    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    
    if total_months < 12:
        return f"{total_months}M"
    else:
        years = total_months // 12
        remaining_months = total_months % 12
        if remaining_months == 0:
            return f"{years}Y"
        else:
            return f"{years}Y {remaining_months}M"

def generate_html(resume_data: Dict) -> str:
    """Generate HTML from JSON Resume data"""
    
    # CSS styles (same as before)
    css = """
  @import url(https://themes.googleusercontent.com/fonts/css?kit=xTOoZr6X-i3kNg7pYrzMsnEzyYBuwf3lO_Sc3Mw9RUVbV0WvE1cEyAoIq5yYZlSc);
  body { background:#fff; margin:0; font-family:"Lato", Arial, sans-serif; color:#000;}
  .doc-content { max-width: 820px; padding:36pt 54pt; margin:0 auto;}
  h1 { font-family:"Raleway"; font-weight:700; font-size:12pt; margin:0 0 4pt 0;}
  h2 { font-family:"Lato"; font-weight:700; font-size:11pt; margin:0 0 4pt 0;}
  h3 { font-family:"Lato"; font-weight:400; font-size:9pt; color:#666; margin:0 0 6pt 0;}
  .title { font-family:"Raleway"; font-weight:700; font-size:24pt; line-height:1.0; margin:0;}
  .subtitle { font-family:"Raleway"; font-weight:700; font-size:16pt; color:#f2511b; margin:3pt 0 0 0;}
  .section { margin-top:18pt; background:#f8f9fa; border-radius:8px; padding:18pt; border:1px solid #e9ecef; }
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
  .skill-group-title { font-size:10pt; font-weight:600; color:#333; margin:8pt 0 4pt 0; }
  .skill-group { margin-bottom:8pt; }
  .contact a { color:inherit; text-decoration:none; }
  .contact a:hover { text-decoration:underline; }
    """
    
    basics = resume_data.get('basics', {})
    
    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '  <meta charset="utf-8">',
        f'  <title>{basics.get("name", "")} — CV</title>',
        '  <meta content="text/html; charset=UTF-8" http-equiv="content-type">',
        f'  <style type="text/css">{css}</style>',
        '</head>',
        '<body>',
        '  <div class="doc-content">'
    ]
    
    # Header section
    html_parts.extend([
        '    <div class="two-col">',
        '      <div>',
        f'        <div class="title">{basics.get("name", "")}</div>',
        f'        <div class="subtitle">{basics.get("label", "")}</div>',
        '      </div>',
        '      <div class="contact small">',
        f'        <p><span class="accent"><a href="mailto:{basics.get("email", "")}">{basics.get("email", "")}</a></span></p>'
    ])
    
    # Add GitHub profile if available
    github_profile = None
    for profile in basics.get('profiles', []):
        if profile.get('network', '').lower() == 'github':
            github_profile = profile.get('url', '')
            break
    
    if github_profile:
        html_parts.append(f'        <p><span class="accent"><a href="{github_profile}">{github_profile}</a></span></p>')
    
    html_parts.extend([
        '      </div>',
        '    </div>'
    ])
    
    # Overview section
    if basics.get('summary'):
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Overview</h1>',
            f'      <p class="small">{basics["summary"]}</p>'
        ])
        
        # Add responsibilities (hardcoded for now, could be dynamic)
        html_parts.extend([
            '',
            '      <h2 class="muted">Responsibilities</h2>',
            '      <ul class="small">',
            '        <li><strong>Data strategy</strong>: Tooling selection, data acquisition, delivery roadmaps & prioritisation.</li>',
            '        <li><strong>Delivery</strong>: Scope & design, stakeholder co‑creation, hands‑on implementation, evaluation.</li>',
            '        <li><strong>Operations</strong>: Team hiring & mentoring, vendor management, enabling self‑sufficient ops.</li>',
            '      </ul>',
            '',
            '      <div class="hr"></div>'
        ])
        
        # Add domain experience (hardcoded for now)
        html_parts.extend([
            '      <h2 class="muted">Domain Experience</h2>',
            '      <ul class="small">',
            '        <li>Healthcare & life sciences: clinical data, EHR/FHIR, women\'s health, R&D analytics.</li>',
            '        <li>Pharmaceutical: manufacturing, clinical trial optimisation, field/sales effectiveness.</li>',
            '        <li>Public sector: DWP, MoD, Home Office (digital transformation, fraud/error analytics).</li>',
            '        <li>Finance & marketing analytics.</li>',
            '      </ul>',
            '',
            '      <div class="hr"></div>'
        ])
        
        # Skills section as grouped pills
        skills = resume_data.get('skills', [])
        if skills:
            html_parts.append('      <h2 class="muted">Key technology skills</h2>')
            
            for skill_group in skills:
                group_name = skill_group.get('name', '')
                keywords = skill_group.get('keywords', [])
                
                if group_name and keywords:
                    html_parts.extend([
                        f'      <h3 class="skill-group-title">{group_name}</h3>',
                        '      <div class="skill-group small">'
                    ])
                    for skill in keywords:
                        html_parts.append(f'        <span class="pill">{skill}</span>')
                    html_parts.append('      </div>')
        
        html_parts.append('    </div>')
    
    # Experience section
    work_experience = resume_data.get('work', [])
    if work_experience:
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Experience</h1>'
        ])
        
        for job in work_experience:
            company = job.get('name', '')
            position = job.get('position', '')
            start_date = job.get('startDate', '')
            end_date = job.get('endDate', '')
            location = job.get('location', '')
            summary = job.get('summary', '')
            highlights = job.get('highlights', [])
            
            # Format duration and dates
            duration = calculate_duration(start_date, end_date)
            date_range = format_date_range(start_date, end_date)
            location_str = f", {location}" if location else ""
            
            html_parts.extend([
                '',
                '      <div class="role">',
                f'        <h2>{company} / <span class="muted">{position}</span></h2>',
                f'        <h3>{duration}: {date_range}{location_str}</h3>',
                f'        <p class="small">{summary}</p>'
            ])
            
            if highlights:
                html_parts.extend([
                    '        <h2 class="muted">Highlights</h2>',
                    '        <ul class="small">'
                ])
                for highlight in highlights:
                    # Convert markdown bold to HTML
                    highlight_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', highlight)
                    html_parts.append(f'          <li>{highlight_html}</li>')
                html_parts.append('        </ul>')
            
            html_parts.append('      </div>')
        
        html_parts.append('    </div>')
    
    # Education section
    education = resume_data.get('education', [])
    if education:
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Education</h1>'
        ])
        
        for edu in education:
            institution = edu.get('institution', '')
            area = edu.get('area', '')
            study_type = edu.get('studyType', '')
            start_date = edu.get('startDate', '')
            end_date = edu.get('endDate', '')
            location = edu.get('location', '')
            summary = edu.get('summary', '')
            
            # Format dates
            date_range = format_date_range(start_date, end_date)
            location_str = f", {location}" if location else ""
            degree_info = f"{area} {study_type}" if area and study_type else (area or study_type or '')
            
            html_parts.extend([
                '      <div class="role">',
                f'        <h2>{institution} / <span class="muted">{degree_info}</span></h2>',
                f'        <h3>{date_range}{location_str}</h3>',
                f'        <p class="small">{summary}</p>',
                '      </div>'
            ])
        
        html_parts.append('    </div>')
    
    # Publications section
    publications = resume_data.get('publications', [])
    if publications:
        html_parts.extend([
            '',
            '    <div class="section">',
            '      <h1>Publications</h1>'
        ])
        
        for pub in publications:
            name = pub.get('name', '')
            publisher = pub.get('publisher', '')
            release_date = pub.get('releaseDate', '')
            url = pub.get('url', '')
            
            # Format the date (assuming YYYY-MM-DD format)
            formatted_date = ''
            if release_date:
                try:
                    # Parse the date and format it
                    if '-' in release_date:
                        date_parts = release_date.split('-')
                        if len(date_parts) >= 2:
                            year = date_parts[0]
                            month = date_parts[1]
                            month_abbrevs = {
                                '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
                                '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
                                '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'
                            }
                            formatted_date = f"{month_abbrevs.get(month, month.upper())} {year}"
                        else:
                            formatted_date = release_date
                    else:
                        formatted_date = release_date
                except:
                    formatted_date = release_date
            
            # Build the publication entry
            html_parts.extend([
                '      <div class="role">',
                f'        <h2>{name}</h2>',
                f'        <h3>{publisher}' + (f', {formatted_date}' if formatted_date else '') + '</h3>'
            ])
            
            if url:
                html_parts.append(f'        <p class="small"><span class="accent"><a href="{url}">{url}</a></span></p>')
            
            html_parts.append('      </div>')
        
        html_parts.append('    </div>')
    
    # Close HTML
    html_parts.extend([
        '  </div>',
        '</body>',
        '</html>'
    ])
    
    return '\n'.join(html_parts)

def main():
    """Main function to generate CV HTML from JSON Resume"""
    resume_path = Path('resume.json')
    output_path = Path('index.html')
    
    if not resume_path.exists():
        print(f"Error: {resume_path} not found")
        return
    
    # Load JSON Resume data
    resume_data = load_resume_data(resume_path)
    
    # Generate HTML
    html = generate_html(resume_data)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated {output_path} from {resume_path}")

if __name__ == '__main__':
    main()