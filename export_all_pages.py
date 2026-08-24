import os
import sys
import time
import json
import base64
import subprocess
import threading
import asyncio
import requests
import websockets

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from PIL import Image

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots_output")
DOCS_DIR = os.path.join(BASE_DIR, "static", "docs")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

PAGES = [
    {"id": "home", "title": "Home Page", "route": "/", "category": "Landing & Bio"},
    {"id": "projects", "title": "Projects Showcase", "route": "/projects", "category": "Curated Engineering & UI/UX"},
    {"id": "skills", "title": "Technical Skills Matrix", "route": "/skills", "category": "Core Competencies"},
    {"id": "certifications", "title": "Certifications & Credentials", "route": "/certifications", "category": "Verified Accreditations"},
    {"id": "contact", "title": "About Me & Contact Hub", "route": "/contact me", "category": "Experience & Inquiries"}
]

CDP_PORT = 9225
FLASK_PORT = 5055

def start_flask():
    from app import app
    app.run(port=FLASK_PORT, debug=False, use_reloader=False)

async def capture_all_cdp():
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-sandbox"
    ])
    
    await asyncio.sleep(2)
    
    try:
        r = requests.get(f"http://127.0.0.1:{CDP_PORT}/json")
        targets = r.json()
        ws_url = targets[0]["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url, max_size=100_000_000) as ws:
            msg_id = 1
            
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                msg_id += 1
                await ws.send(json.dumps(cmd))
                while True:
                    raw = await ws.recv()
                    res = json.loads(raw)
                    if res.get("id") == cmd["id"]:
                        if "error" in res:
                            print(f"Error in {method}: {res['error']}")
                            return {}
                        return res.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("DOM.enable")

            results = []

            for page in PAGES:
                url = f"http://127.0.0.1:{FLASK_PORT}{page['route']}"
                print(f"Loading {url}...")
                await send_cmd("Page.navigate", {"url": url})
                await asyncio.sleep(2.5)  # Wait for CSS animations & fonts to render

                # Get actual full document height
                eval_res = await send_cmd("Runtime.evaluate", {
                    "expression": "JSON.stringify({width: 1440, height: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)})"
                })
                dims = json.loads(eval_res.get("result", {}).get("value", '{"width":1440,"height":1080}'))
                full_width = dims.get("width", 1440)
                full_height = dims.get("height", 1080)
                print(f"   Measured page dimensions: {full_width}x{full_height}px")

                # Set device metrics to full page
                await send_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": full_width,
                    "height": full_height,
                    "deviceScaleFactor": 1.2,
                    "mobile": False
                })
                await asyncio.sleep(1.0)

                # 1. Full Height Screenshot
                shot_res = await send_cmd("Page.captureScreenshot", {
                    "format": "png",
                    "captureBeyondViewport": True
                })
                
                full_shot_path = os.path.join(SCREENSHOTS_DIR, f"full_{page['id']}.png")
                if "data" in shot_res:
                    with open(full_shot_path, "wb") as f:
                        f.write(base64.b64decode(shot_res["data"]))
                
                # Check dimensions
                img = Image.open(full_shot_path)
                print(f"   [OK] Saved FULL screenshot {full_shot_path} (Dimensions: {img.size[0]}x{img.size[1]})")

                # 2. Native Vector PDF Print from Chrome
                pdf_res = await send_cmd("Page.printToPDF", {
                    "printBackground": True,
                    "paperWidth": 8.5,
                    "paperHeight": 11.0,
                    "marginTop": 0.3,
                    "marginBottom": 0.3,
                    "marginLeft": 0.3,
                    "marginRight": 0.3,
                    "scale": 0.95
                })
                page_pdf_path = os.path.join(DOCS_DIR, f"{page['id']}_print.pdf")
                if "data" in pdf_res:
                    with open(page_pdf_path, "wb") as f:
                        f.write(base64.b64decode(pdf_res["data"]))
                    print(f"   [OK] Generated Chrome Vector PDF for {page['title']}")

                results.append({
                    "page": page,
                    "screenshot_path": full_shot_path,
                    "pdf_path": page_pdf_path,
                    "width": img.size[0],
                    "height": img.size[1]
                })

            return results
    finally:
        chrome_proc.terminate()

def create_master_pdf(capture_results):
    """Creates a high quality multi-page PDF document with full screenshots & traceability without squishing."""
    final_pdf_path = os.path.join(DOCS_DIR, "Portfolio_Complete_Export.pdf")
    root_final_pdf_path = os.path.join(BASE_DIR, "Portfolio_Complete_Export.pdf")

    # We will build a clean multi-page document
    # Standard Letter: 612 x 792 pt, margins 36pt -> printable width = 540pt, height = 720pt
    doc = SimpleDocTemplate(
        final_pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#00f2fe")
    )
    subtitle_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#cbd5e1")
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#ffffff"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#38bdf8"),
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#e2e8f0")
    )

    class CustomCanvas(canvas.Canvas):
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
                self.draw_bg_and_footer(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_bg_and_footer(self, page_count):
            self.saveState()
            self.setFillColor(colors.HexColor("#0a0b10"))
            self.rect(0, 0, self._pagesize[0], self._pagesize[1], fill=True, stroke=False)
            
            # Header line
            self.setStrokeColor(colors.HexColor("#1e2238"))
            self.setLineWidth(0.75)
            self.line(36, self._pagesize[1] - 30, self._pagesize[0] - 36, self._pagesize[1] - 30)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#00f2fe"))
            self.drawString(36, self._pagesize[1] - 24, "SIDDHARTH MV")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#94a3b8"))
            self.drawString(110, self._pagesize[1] - 24, "| Portfolio Full UI Traceability Export")
            
            # Footer
            self.line(36, 30, self._pagesize[0] - 36, 30)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(36, 18, "Exported with Full Resolution & Traceability")
            self.drawRightString(self._pagesize[0] - 36, 18, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()

    story = []

    # 1. Title / Cover Section
    story.append(Spacer(1, 20))
    story.append(Paragraph("Siddharth MV — Portfolio UI & Architecture Export", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Complete full-resolution visual export with comprehensive traceability across all portfolio routes, components, design tokens, and responsive UI layouts.",
        subtitle_style
    ))
    story.append(Spacer(1, 14))

    # Summary table
    table_rows = [
        [Paragraph("<b>Page Name</b>", cell_style), Paragraph("<b>Route</b>", cell_style), Paragraph("<b>Category</b>", cell_style), Paragraph("<b>Full Captured Dimensions</b>", cell_style)]
    ]
    for res in capture_results:
        p = res["page"]
        table_rows.append([
            Paragraph(f"<b>{p['title']}</b>", cell_style),
            Paragraph(f"<code>{p['route']}</code>", cell_style),
            Paragraph(p["category"], cell_style),
            Paragraph(f"{res['width']} × {res['height']} px (100% full-height)", cell_style)
        ])
    
    t = Table(table_rows, colWidths=[140, 100, 140, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#161a2e")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#101322")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#272d4a")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e2338")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(PageBreak())

    # 2. For each page, split screenshot cleanly into page-sized slices so NOTHING is squished or distorted!
    usable_width = 540  # points
    usable_height = 680 # points
    
    for res in capture_results:
        p = res["page"]
        img_path = res["screenshot_path"]
        pil_img = Image.open(img_path)
        img_w, img_h = pil_img.size

        # We want the width to fit 540 pt.
        # Ratio:
        scale = usable_width / img_w
        rendered_total_h = img_h * scale

        story.append(Paragraph(f"{p['title']} — Full Webpage Capture", h1_style))
        story.append(Paragraph(f"Route: <code>{p['route']}</code> | Category: {p['category']} | Native Resolution: {img_w}x{img_h}px", h2_style))
        story.append(Spacer(1, 6))

        # If rendered height fits within single page (with header ~620pt), place it directly
        if rendered_total_h <= 620:
            story.append(RLImage(img_path, width=usable_width, height=rendered_total_h))
            story.append(PageBreak())
        else:
            # Slice image vertically so every slice renders at 100% natural resolution across multiple pages without squishing!
            slice_h_px = int(usable_height / scale)
            num_slices = (img_h + slice_h_px - 1) // slice_h_px
            
            for s_idx in range(num_slices):
                top_y = s_idx * slice_h_px
                bottom_y = min((s_idx + 1) * slice_h_px, img_h)
                
                cropped = pil_img.crop((0, top_y, img_w, bottom_y))
                slice_path = os.path.join(SCREENSHOTS_DIR, f"slice_{p['id']}_{s_idx}.png")
                cropped.save(slice_path)
                
                slice_rendered_h = (bottom_y - top_y) * scale
                
                if s_idx > 0:
                    story.append(Paragraph(f"{p['title']} (Part {s_idx + 1} of {num_slices})", h2_style))
                    story.append(Spacer(1, 4))
                
                story.append(RLImage(slice_path, width=usable_width, height=slice_rendered_h))
                story.append(PageBreak())

    doc.build(story, canvasmaker=CustomCanvas)

    import shutil
    shutil.copyfile(final_pdf_path, root_final_pdf_path)
    # Also update Portfolio_UI_Traceability_Report.pdf so both names are populated
    shutil.copyfile(final_pdf_path, os.path.join(BASE_DIR, "Portfolio_UI_Traceability_Report.pdf"))
    shutil.copyfile(final_pdf_path, os.path.join(DOCS_DIR, "Portfolio_UI_Traceability_Report.pdf"))

    print(f"Successfully generated master PDF:")
    print(f" -> {final_pdf_path}")
    print(f" -> {root_final_pdf_path}")

def main():
    print("Starting Flask server...")
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()
    time.sleep(2)

    print("Running CDP Full-Page Capture...")
    results = asyncio.run(capture_all_cdp())

    print("Building Master Multi-Page PDF...")
    create_master_pdf(results)
    print("ALL DONE!")

if __name__ == "__main__":
    main()
