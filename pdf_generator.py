"""
PDF and HTML Generator for Legal Content
Converts markdown legal articles to formatted PDF or HTML
"""

def generate_pdf(content):
    """
    Generate PDF from markdown content
    
    Args:
        content (str): Markdown formatted text
        
    Returns:
        bytes: PDF file as bytes, or None if generation fails
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        import io
        import re
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=50, 
            leftMargin=50, 
            topMargin=50, 
            bottomMargin=30
        )
        
        # Container for content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom style for body text (left-aligned)
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            alignment=TA_LEFT,
            fontSize=11,
            leading=14,
            spaceAfter=6
        ))
        
        # Process markdown content line by line
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.1*inch))
                continue
            
            # Convert markdown bold to reportlab bold (**text** -> <b>text</b>)
            line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            
            # Handle headers
            if line.startswith('# '):
                text = line[2:]
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(text, styles['Heading1']))
                story.append(Spacer(1, 0.15*inch))
                
            elif line.startswith('## '):
                text = line[3:]
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(text, styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
                
            elif line.startswith('### '):
                text = line[4:]
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(text, styles['Heading3']))
                story.append(Spacer(1, 0.08*inch))
                
            # Handle bullet points
            elif line.startswith('• ') or line.startswith('- ') or line.startswith('* '):
                text = line[2:]
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                story.append(Paragraph(f'• {text}', styles['CustomBody']))
                
            # Regular paragraph
            else:
                story.append(Paragraph(line, styles['CustomBody']))
                story.append(Spacer(1, 0.08*inch))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except ImportError as e:
        print(f"❌ PDF generation requires: pip install reportlab")
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None


def generate_html(content):
    """
    Generate clean HTML from markdown content (ready for WordPress/CMS)
    
    Args:
        content (str): Markdown formatted text
        
    Returns:
        str: HTML formatted text
    """
    import re
    
    html_lines = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            html_lines.append('<br>')
            continue
        
        # Convert markdown bold to HTML strong
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        
        # Handle headers
        if line.startswith('# '):
            text = line[2:]
            html_lines.append(f'<h1>{text}</h1>')
            
        elif line.startswith('## '):
            text = line[3:]
            html_lines.append(f'<h2>{text}</h2>')
            
        elif line.startswith('### '):
            text = line[4:]
            html_lines.append(f'<h3>{text}</h3>')
            
        # Handle bullet points
        elif line.startswith('• ') or line.startswith('- ') or line.startswith('* '):
            text = line[2:]
            html_lines.append(f'<li>{text}</li>')
            
        # Regular paragraph
        else:
            html_lines.append(f'<p>{line}</p>')
    
    return '\n'.join(html_lines)