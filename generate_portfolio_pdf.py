import os
import sys
import time
import subprocess
import threading
from datetime import datetime
from PIL import Image

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots_output")
DOCS_DIR = os.path.join(BASE_DIR, "static", "docs")
PDF_OUTPUT_PATH = os.path.join(DOCS_DIR, "Portfolio_UI_Traceability_Report.pdf")
ROOT_PDF_OUTPUT_PATH = os.path.join(BASE_DIR, "Portfolio_UI_Traceability_Report.pdf")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

def find_browser():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None

PAGES_CONFIG = [
    {
        "id": "home",
        "title": "Home Page (Hero, Highlights & Quick Bio)",
        "route": "/",
        "category": "Core Landing",
        "description": "Primary landing showcase with dynamic ambient glowing orbs, animated headline, featured project previews, technical skill badges, and quick contact call-to-action.",
        "components": [
            "Glass Header Navigation with active page pills",
            "Hero Section: Name title, tagline badge, action buttons (Explore Work / Get In Touch)",
            "Ambient Glow Canvas (CSS radial gradient orbs)",
            "Quick Stats & Highlight Cards",
            "Featured Works Carousel / Grid Preview",
            "Glassmorphic Footer with social badges & sitemap"
        ],
        "design_tokens": {
            "Background": "#0a0b10 (Deep Void)",
            "Primary Accent": "#00f2fe -> #4facfe (Electric Cyan Gradient)",
            "Card Fill": "rgba(18, 20, 32, 0.65) with 1px backdrop-filter blur(16px)",
            "Typography": "Outfit (Headings) & Inter (Body Text)"
        }
    },
    {
        "id": "projects",
        "title": "Projects Showcase & Dynamic Filter Matrix",
        "route": "/projects",
        "category": "Portfolio Work",
        "description": "Comprehensive interactive project catalog with category filtering (All, UI/UX Design, Full Stack, Web Apps, AI & Data), live demo buttons, GitHub repo links, and technology tags.",
        "components": [
            "Filter Tab Bar with dynamic counters & active state highlighting",
            "Responsive Project Card Grid with hover tilt & glow effects",
            "Project Meta Tags (Figma, Django, Python, TypeScript, CodeMirror 6, etc.)",
            "Feature Bullet Highlight Lists per card",
            "External Action Links (Live Demo, GitHub Source, Figma Prototype)"
        ],
        "design_tokens": {
            "Filter Pill Active": "Linear Gradient (#00f2fe to #6366f1) + Glow shadow",
            "Card Border": "rgba(255, 255, 255, 0.08) hover rgba(0, 242, 254, 0.4)",
            "Tag Badges": "rgba(99, 102, 241, 0.15) with #a5b4fc text"
        }
    },
    {
        "id": "skills",
        "title": "Technical Skills & Competency Matrix",
        "route": "/skills",
        "category": "Capabilities",
        "description": "Structured domain-specific taxonomy showcasing core engineering, design systems, databases, cloud, and DevOps tooling.",
        "components": [
            "Category Group Cards: Programming Languages, Frameworks, UI/UX Design, Databases, DevOps",
            "Category Header Icons (SVG Code, Layers, Figma, Database, Terminal)",
            "Interactive Skill Pills with neon accent hover highlights",
            "Competency proficiency badges and experience descriptors"
        ],
        "design_tokens": {
            "Category Card": "Glass morphism with subtle gradient headers",
            "Skill Badge": "#1e2238 with #38bdf8 border-hover glow"
        }
    },
    {
        "id": "certifications",
        "title": "Certifications & Verified Credentials",
        "route": "/certifications",
        "category": "Credentials",
        "description": "Verified academic and industrial certifications with credential badges, issuing organizations (Tutedude, Cisco, Teachnook, Coursera), dates, and direct Google Drive archive integration.",
        "components": [
            "Google Drive Certificate Archive Header Banner & Direct Access Button",
            "Certification Grid Cards with Issuer Logos & Date Badges",
            "Domain Category Badges (DevOps & Cloud, UI/UX, Data Analytics, Full Stack)",
            "Curriculum Summary bullet points"
        ],
        "design_tokens": {
            "Drive Button": "Gradient Button with drive folder icon & glow",
            "Issuer Tag": "rgba(56, 189, 248, 0.12) with #38bdf8"
        }
    },
    {
        "id": "contact",
        "title": "About Me & Contact Hub",
        "route": "/contact me",
        "category": "Communication & Bio",
        "description": "Detailed background biography, career philosophy, educational milestones, interactive contact form, and direct social profile connectors.",
        "components": [
            "Biography Overview Card with developer identity philosophy",
            "Education & Career Milestone timeline cards",
            "Contact Form with styled inputs, focus glow, and submission handlers",
            "Social Channel Links (GitHub, LinkedIn, Email, Drive)"
        ],
        "design_tokens": {
            "Form Inputs": "rgba(255, 255, 255, 0.05) with #00f2fe focus border",
            "Submit CTA": "Full-width gradient button with micro-animation"
        }
    }
]

def run_flask_in_thread(port=5050):
    from app import app
    app.run(port=port, debug=False, use_reloader=False)

def capture_screenshot(browser_path, url, output_img_path, width=1440, height=900, is_mobile=False):
    """Captures a screenshot using headless Chrome/Edge."""
    cmd = [
        browser_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1.2",
        f"--window-size={width},{height}",
        "--default-background-color=0a0b10",
        "--virtual-time-budget=2500",
        f"--screenshot={output_img_path}",
        url
    ]
    if is_mobile:
        cmd.insert(4, "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1")
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

class NumberedCanvas(canvas.Canvas):
    """Canvas that adds running headers, dark styling and accurate page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, page_count):
        # Draw background color
        self.saveState()
        self.setFillColor(colors.HexColor("#0d0f18"))
        self.rect(0, 0, self._pagesize[0], self._pagesize[1], fill=True, stroke=False)
        
        # Don't draw header/footer on cover page (page 1)
        if self._pageNumber > 1:
            # Header rule & title
            self.setStrokeColor(colors.HexColor("#222638"))
            self.setLineWidth(0.75)
            self.line(40, self._pagesize[1] - 38, self._pagesize[0] - 40, self._pagesize[1] - 38)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#00f2fe"))
            self.drawString(40, self._pagesize[1] - 32, "SIDDHARTH MV")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#8e95b0"))
            self.drawString(115, self._pagesize[1] - 32, "|  Portfolio UI & Architecture Traceability Report")
            
            # Footer rule & page numbering
            self.line(40, 38, self._pagesize[0] - 40, 38)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(40, 26, f"Generated on {datetime.now().strftime('%B %d, %Y')} | UI Traceability Spec")
            
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(self._pagesize[0] - 40, 26, page_text)
            
        self.restoreState()

def build_pdf_report():
    browser = find_browser()
    if not browser:
        print("Error: Chrome or Edge executable not found for screenshot capture!")
        sys.exit(1)

    port = 5050
    print(f"[1/4] Starting background Flask server on port {port}...")
    server_thread = threading.Thread(target=run_flask_in_thread, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(2)  # wait for Flask to bind

    print("[2/4] Capturing full-fidelity webpage screenshots (Desktop & Mobile)...")
    screenshot_records = []
    base_url = f"http://127.0.0.1:{port}"

    for page in PAGES_CONFIG:
        url = f"{base_url}{page['route']}"
        desktop_img_name = f"screen_{page['id']}_desktop.png"
        mobile_img_name = f"screen_{page['id']}_mobile.png"
        
        desktop_path = os.path.join(SCREENSHOTS_DIR, desktop_img_name)
        mobile_path = os.path.join(SCREENSHOTS_DIR, mobile_img_name)
        
        # Capture Desktop (1440x950)
        capture_screenshot(browser, url, desktop_path, width=1440, height=950, is_mobile=False)
        # Capture Mobile (390x844)
        capture_screenshot(browser, url, mobile_path, width=390, height=844, is_mobile=True)
        
        screenshot_records.append({
            "config": page,
            "desktop_path": desktop_path,
            "mobile_path": mobile_path
        })
        print(f"   [OK] Captured {page['title']} ({page['route']})")

    print("[3/4] Compiling UI Traceability Analysis & PDF Document...")
    
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    # Custom dark-theme styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#ffffff"),
        alignment=0
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#00f2fe"),
        alignment=0
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#ffffff"),
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#00f2fe"),
        spaceBefore=8,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#cbd5e1")
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#38bdf8")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#00f2fe")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#e2e8f0")
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("<font color='#00f2fe'>&lt;S/&gt;</font> PORTFOLIO SYSTEM SPECIFICATION", cover_subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Webpage UI Traceability &<br/>Visual Architecture Report", cover_title_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "A comprehensive high-fidelity visual and technical traceability audit of the Siddharth MV portfolio application. "
        "Capturing page layouts, responsive UI states, color tokens, DOM components, and interaction patterns.",
        body_style
    ))
    story.append(Spacer(1, 24))

    # Meta Overview Box
    meta_data = [
        [Paragraph("<b>Project:</b>", table_header_style), Paragraph("Siddharth MV Portfolio Web Application", table_cell_style)],
        [Paragraph("<b>Tech Stack:</b>", table_header_style), Paragraph("Flask, Python 3.11, HTML5, CSS3 Glassmorphism, JavaScript", table_cell_style)],
        [Paragraph("<b>Author / Engineer:</b>", table_header_style), Paragraph("Siddharth MV (@siddharthx29)", table_cell_style)],
        [Paragraph("<b>Audit Date:</b>", table_header_style), Paragraph(datetime.now().strftime("%B %d, %Y"), table_cell_style)],
        [Paragraph("<b>Scope:</b>", table_header_style), Paragraph("5 Primary Routes, Category Matrix, Responsive Viewports (Desktop 1440px / Mobile 390px)", table_cell_style)],
        [Paragraph("<b>Live Target:</b>", table_header_style), Paragraph("http://127.0.0.1:5050 / Vercel Production", table_cell_style)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 390])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#141724")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#262a40")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e2236")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 28))

    # Design System Tokens Box
    story.append(Paragraph("Design System & Color Tokens", h2_style))
    tokens_data = [
        [
            Paragraph("<b>Deep Void</b><br/><font color='#94a3b8'>#0a0b10 (Base Canvas)</font>", table_cell_style),
            Paragraph("<b>Electric Cyan</b><br/><font color='#00f2fe'>#00f2fe (Primary Accent)</font>", table_cell_style),
            Paragraph("<b>Royal Indigo</b><br/><font color='#6366f1'>#6366f1 (Secondary Accent)</font>", table_cell_style),
            Paragraph("<b>Glass Card</b><br/><font color='#cbd5e1'>rgba(18,20,32,0.65)</font>", table_cell_style)
        ]
    ]
    tokens_table = Table(tokens_data, colWidths=[127, 127, 127, 127])
    tokens_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#0a0b10")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#06283d")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#1e1b4b")),
        ('BACKGROUND', (3,0), (3,0), colors.HexColor("#121420")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2d334d")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#22263a")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tokens_table)
    story.append(PageBreak())

    # ================= UI TRACEABILITY MATRIX =================
    story.append(Paragraph("1. Complete UI Traceability Matrix", h1_style))
    story.append(Paragraph(
        "This matrix details every page, route, visual component breakdown, interaction handlers, and responsive layout behavior across the application.",
        body_style
    ))
    story.append(Spacer(1, 12))

    matrix_rows = [
        [
            Paragraph("<b>Page / Route</b>", table_header_style),
            Paragraph("<b>UI Components & Elements</b>", table_header_style),
            Paragraph("<b>Interactivity & Handlers</b>", table_header_style),
            Paragraph("<b>Design Pattern</b>", table_header_style)
        ]
    ]

    for p in PAGES_CONFIG:
        comp_str = "<br/>• ".join([""] + p["components"])
        matrix_rows.append([
            Paragraph(f"<b>{p['title']}</b><br/><font color='#00f2fe'><code>{p['route']}</code></font><br/><font color='#64748b'>({p['category']})</font>", table_cell_style),
            Paragraph(f"<font color='#cbd5e1'>{comp_str}</font>", table_cell_style),
            Paragraph("Hover glow states, active route highlight, dynamic client links, responsive layout toggle.", table_cell_style),
            Paragraph("Glassmorphism, CSS Grid & Flexbox, Ambient Canvas Radial Orbs.", table_cell_style)
        ])

    matrix_table = Table(matrix_rows, colWidths=[110, 180, 110, 110])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#161a2b")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#0f121d")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#2a3047")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1c2033")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(matrix_table)
    story.append(PageBreak())

    # ================= PAGE-BY-PAGE SCREENSHOT SHOWCASE & TRACEABILITY =================
    for idx, rec in enumerate(screenshot_records, start=2):
        p_cfg = rec["config"]
        story.append(Paragraph(f"{idx}. Page Traceability: {p_cfg['title']}", h1_style))
        story.append(Paragraph(f"<b>Route:</b> <font color='#00f2fe'><code>{p_cfg['route']}</code></font> &nbsp;|&nbsp; <b>Category:</b> {p_cfg['category']}", h2_style))
        story.append(Paragraph(p_cfg["description"], body_style))
        story.append(Spacer(1, 8))

        # Add Desktop Screenshot
        if os.path.exists(rec["desktop_path"]):
            # Target width in PDF is ~510pt, height proportional
            story.append(Paragraph("<b>Desktop Viewport (1440x950) — Full UI Composition</b>", badge_style))
            story.append(Spacer(1, 4))
            story.append(RLImage(rec["desktop_path"], width=510, height=270))
            story.append(Spacer(1, 8))

        # Bottom row: Component breakdown & Mobile preview
        detail_data = [
            [
                Paragraph("<b>Component Hierarchy & DOM Elements:</b><br/>" + "<br/>".join([f"• {c}" for c in p_cfg["components"]]), table_cell_style),
                Paragraph("<b>Mobile UI (390px):</b>", badge_style)
            ]
        ]
        
        # Create a mini table to pair component details with mobile screenshot
        mobile_flowable = RLImage(rec["mobile_path"], width=130, height=210) if os.path.exists(rec["mobile_path"]) else Paragraph("N/A", table_cell_style)
        
        spec_table = Table([
            [
                Paragraph(
                    f"<b>Design & Layout Specifications:</b><br/>"
                    f"• <b>Route Endpoint:</b> <code>{p_cfg['route']}</code><br/>"
                    f"• <b>Semantic Structure:</b> <code>&lt;header&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;section&gt;</code>, <code>&lt;footer&gt;</code><br/>"
                    f"• <b>UI Tokens:</b> {', '.join([f'{k}: {v}' for k, v in p_cfg['design_tokens'].items()])}<br/>"
                    f"• <b>Key Elements:</b><br/>" + "<br/>".join([f"&nbsp;&nbsp;- {c}" for c in p_cfg["components"][:4]]),
                    table_cell_style
                ),
                mobile_flowable
            ]
        ], colWidths=[360, 150])
        
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#121524")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#24293f")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1a1e30")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'CENTER')
        ]))
        
        story.append(spec_table)
        story.append(PageBreak())

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Also copy to root for instant access
    import shutil
    shutil.copyfile(PDF_OUTPUT_PATH, ROOT_PDF_OUTPUT_PATH)
    
    print(f"[4/4] Successfully built UI Traceability PDF Report:")
    print(f"   -> {PDF_OUTPUT_PATH}")
    print(f"   -> {ROOT_PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf_report()
