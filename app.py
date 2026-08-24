import os
from flask import Flask, render_template, request, redirect, send_file, abort

# Get the absolute path to the directory where this script is located
basedir = os.path.abspath(os.path.dirname(__file__))
# Ensure the working directory is set to the script's location
os.chdir(basedir)

app = Flask(__name__)

# Curated, authentic projects data from GitHub repositories and Figma
PROJECTS_DATA = [
    {
        "id": "figma-uiux-assignment",
        "title": "Siddharth Assignment",
        "category": "UI/UX Design",
        "category_slug": "uiux",
        "is_featured": True,
        "is_design": True,
        "desc": "A comprehensive UI/UX design project on Figma emphasizing clean design systems, deliberate visual hierarchy, accessible color palettes, responsive web patterns, and interactive user flows.",
        "long_desc": "Built in Figma, this project explores modern interface architecture, user journeys, component modularity, typography hierarchy, and interactive prototypes. It demonstrates end-to-end UX thinking from user problem analysis to high-fidelity, production-ready interface mockups.",
        "tags": ["Figma", "UI/UX Design", "Wireframing", "Interactive Prototyping", "Design Systems", "User Flows"],
        "figma_link": "https://www.figma.com/file/FVWgtwVkiyFNgGoT14e8Wj/Siddharth-Assignment",
        "github_link": None,
        "demo_link": "https://www.figma.com/file/FVWgtwVkiyFNgGoT14e8Wj/Siddharth-Assignment",
        "highlights": [
            "Comprehensive component design system with reusable typography & color tokens",
            "High-fidelity desktop and mobile responsive interface screens",
            "Structured UX layout focusing on conversion paths and reduced cognitive load",
            "Interactive prototyping with realistic states and transitions"
        ]
    },
    {
        "id": "teamnext-erp",
        "title": "TeamNext ERP",
        "category": "Full Stack",
        "category_slug": "fullstack",
        "is_featured": True,
        "is_design": False,
        "desc": "An open-source, full-featured Enterprise Resource Planning (ERP) platform built with Python & Django, integrating HR, Finance, Inventory, Projects, and Payroll management.",
        "long_desc": "TeamNext ERP is an enterprise-scale web application engineered to consolidate business operations into a unified workspace. It handles multi-module workflows including employee records, departmental hierarchies, expense and payroll tracking, inventory balance, and operational project tasks.",
        "tags": ["Python", "Django", "JavaScript", "HTML5", "CSS3", "PostgreSQL / SQLite"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/TeamNext-ERP-Open-Source-Enterprise-Resource-Planning-Management-System.",
        "demo_link": "https://teamnexterp.com/",
        "highlights": [
            "Modular ERP architecture with dedicated HR, Finance, Inventory, and Project suites",
            "Automated payroll calculation and role-based access permission system",
            "Responsive administrative dashboard with operational data metrics",
            "Robust relational database design ensuring transactional consistency"
        ]
    },
    {
        "id": "ihatepdf",
        "title": "ihatepdf – Realtime File Converter",
        "category": "Web Applications",
        "category_slug": "webapp",
        "is_featured": True,
        "is_design": False,
        "desc": "A sleek, all-in-one file format conversion platform built to eliminate subscription paywalls and deliver instantaneous document, image, and data conversions.",
        "long_desc": "ihatepdf provides zero-barrier file conversions across various formats (PDF, Word, Excel, CSV, JSON, images, and media). Built with modern web standards to provide swift in-browser processing without forced logins or file limits.",
        "tags": ["JavaScript", "Node.js", "HTML5", "CSS3", "File APIs", "Web Utilities"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Realtime-file-format-conversions-webapp-IHatePdf-",
        "demo_link": None,
        "highlights": [
            "Multi-format document conversion pipeline (PDF, Word, Sheets, Data formats)",
            "Clean and privacy-first client side workflows with zero paywalls",
            "Intuitive drag-and-drop upload interface with immediate feedback",
            "Lightweight client processing architecture for rapid turnaround"
        ]
    },
    {
        "id": "jupyter-notes-saver",
        "title": "JupyterNotebook Cloud Notes Saver",
        "category": "Web Applications",
        "category_slug": "webapp",
        "is_featured": True,
        "is_design": False,
        "desc": "A high-speed cloud notepad and code preservation webapp featuring byte-for-byte exact code formatting, CodeMirror 6, custom expiry, and optional PIN security.",
        "long_desc": "Engineered for developers who require zero-modification text sharing. Preserves indentation, whitespace, Python syntax, and symbols with 100% fidelity. Provides shareable unique shortcodes and expiration intervals.",
        "tags": ["TypeScript", "CodeMirror 6", "JavaScript", "CSS3", "Vercel"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Jupyter-Notes---Cloud-Notes-Saver",
        "demo_link": "https://jupyterbook.vercel.app",
        "highlights": [
            "100% byte-for-byte exact code formatting with zero unwanted auto-formatting",
            "Integrated CodeMirror 6 editor with interactive syntax highlighting",
            "Configurable expiration intervals (10 mins to 30 days) and custom PIN security",
            "Instant retrieval via concise custom short-links"
        ]
    },
    {
        "id": "bunkermate",
        "title": "BunkerMate Attendance Tracker",
        "category": "Full Stack",
        "category_slug": "fullstack",
        "is_featured": False,
        "is_design": False,
        "desc": "An anonymous, device-based attendance tracking & bunk calculator web application with cloud persistence in PostgreSQL and dynamic analytics.",
        "long_desc": "BunkerMate provides students with smart attendance tracking without cumbersome signup forms. Data is securely linked to unique browser sessions and stored in PostgreSQL, offering real-time threshold calculations.",
        "tags": ["JavaScript", "PostgreSQL", "Node.js / Express", "CSS3", "HTML5"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/BunkerMate",
        "demo_link": None,
        "highlights": [
            "Zero-friction anonymous session tracking linked to browser fingerprints",
            "Intelligent algorithm calculating safe skips versus attendance risk alerts",
            "Persistent cloud storage backed by PostgreSQL database",
            "Interactive dashboard with visual metrics and responsive UI"
        ]
    },
    {
        "id": "library-management",
        "title": "Django Library Management System",
        "category": "Full Stack",
        "category_slug": "fullstack",
        "is_featured": False,
        "is_design": False,
        "desc": "A web application developed with Django and SQLite to automate daily library operations including cataloging, book issuance, return logs, and student records.",
        "long_desc": "Designed to digitize physical library registers for educational institutions. Provides administrators with a secure portal to manage book inventories, track fine penalties, monitor overdue returns, and handle student memberships.",
        "tags": ["Python", "Django", "SQLite", "HTML5", "CSS3", "Bootstrap"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Library-Management-System-Django-",
        "demo_link": None,
        "highlights": [
            "Complete CRUD management for book catalogs, authors, and student profiles",
            "Automated issuance, due date tracking, and overdue status checks",
            "Django ORM and admin dashboard integration for secure operation",
            "Structured relational database schema using SQLite"
        ]
    },
    {
        "id": "grab-a-cab",
        "title": "Grab A Cab – Rental Cab Booking",
        "category": "Web Applications",
        "category_slug": "webapp",
        "is_featured": False,
        "is_design": False,
        "desc": "A responsive cab rental and fare booking web application hosted on Netlify, facilitating seamless route selection, vehicle fleet preview, and booking inquiries.",
        "long_desc": "Developed to provide users with a straightforward interface for exploring rental cab options, calculating approximate trip rates, and viewing fleet options with optimized mobile responsiveness.",
        "tags": ["JavaScript", "HTML5", "CSS3", "Netlify Deployment"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Goa-rentacab",
        "demo_link": "https://grabacab.netlify.app/index.html",
        "highlights": [
            "Dynamic vehicle fleet catalog with pricing tiers and features",
            "Interactive route estimation and reservation inquiry workflow",
            "Mobile-first responsive interface optimized for speed and clarity",
            "Deployed live on Netlify CDN"
        ]
    },
    {
        "id": "weatherifive",
        "title": "WeatheriFive – Forecast App",
        "category": "Web Applications",
        "category_slug": "webapp",
        "is_featured": False,
        "is_design": False,
        "desc": "A real-time weather forecasting web application with dynamic atmospheric metrics, temperature forecasts, and location-based weather tracking.",
        "long_desc": "Consumes live weather API endpoints to present real-time climate conditions, humidity levels, wind vectors, and multi-day forecasts with an intuitive glassmorphic dashboard.",
        "tags": ["JavaScript", "Weather APIs", "CSS3", "HTML5", "Netlify"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Weather-app",
        "demo_link": "https://weatherifive.netlify.app/",
        "highlights": [
            "Real-time weather data fetching via asynchronous API calls",
            "Dynamic visual climate condition indicators and metric badges",
            "Search functionality with responsive error handling for invalid cities",
            "Clean mobile-friendly layout hosted on Netlify"
        ]
    },
    {
        "id": "ai-chatbot",
        "title": "AI Powered Conversational Chatbot",
        "category": "AI & Data",
        "category_slug": "aidata",
        "is_featured": False,
        "is_design": False,
        "desc": "A reusable AI chatbot template featuring real-time message streaming, typing indicators, adaptable theme styling, and easy API integration hooks.",
        "long_desc": "Provides a clean, modular frontend chat interface ready to integrate with AI endpoints (OpenAI, Dialogflow, or custom Python ML backends) for automated customer support and conversational queries.",
        "tags": ["Python", "JavaScript", "CSS3", "HTML5", "AI API Integration"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/AI-powered-Chatbot-",
        "demo_link": None,
        "highlights": [
            "Modern conversation container with typing indicator and auto-scroll",
            "Modular backend architecture designed for OpenAI or custom LLM hooks",
            "Customizable glass UI styling and mobile-responsive layout",
            "Clean message history state management"
        ]
    },
    {
        "id": "earth-parameters",
        "title": "Earth Parameters & Data Analysis",
        "category": "AI & Data",
        "category_slug": "aidata",
        "is_featured": False,
        "is_design": False,
        "desc": "A Python computational analysis project exploring geophysical, atmospheric, and planetary data metrics with statistical computation and visualization.",
        "long_desc": "Utilizes Python scientific computation tooling to analyze numerical datasets, generate trend charts, and model environmental parameter variations.",
        "tags": ["Python", "Data Analysis", "Numerical Computing", "Jupyter"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/Earth_Parameters-Analysis",
        "demo_link": None,
        "highlights": [
            "Exploratory data analysis on atmospheric and geophysical variables",
            "Statistical computing workflows using Python libraries",
            "Data visualization charts for scientific metrics",
            "Structured research codebase on GitHub"
        ]
    },
    {
        "id": "taskflow",
        "title": "TaskFlow Task Manager",
        "category": "Full Stack",
        "category_slug": "fullstack",
        "is_featured": False,
        "is_design": False,
        "desc": "An open-source task management system designed to organize daily workflows, prioritize objectives, and track task completions with persistent storage.",
        "long_desc": "TaskFlow provides an organized board for managing task lifecycles, editing priorities, filtering pending vs completed tasks, and ensuring state persistence.",
        "tags": ["Python", "Django", "JavaScript", "HTML5", "CSS3", "SQLite"],
        "figma_link": None,
        "github_link": "https://github.com/siddharthx29/TaskFlow-Open-Source-Task-Management-System.",
        "demo_link": None,
        "highlights": [
            "Full task lifecycle handling (Add, Edit, Mark Complete, Remove)",
            "Categorized views for pending and completed activities",
            "Persistent SQLite storage via Django backend",
            "Responsive task board interface"
        ]
    }
]

# Categorized skills verified from GitHub repos and academic training
SKILLS_DATA = {
    "languages": {
        "title": "Programming & Web Languages",
        "icon": "code",
        "skills": ["Python", "JavaScript", "TypeScript", "Java", "C Programming", "SQL / PL-SQL", "HTML5", "CSS3"]
    },
    "frameworks": {
        "title": "Frameworks & Libraries",
        "icon": "layers",
        "skills": ["Django", "Flask", "Node.js", "Express", "CodeMirror 6", "RESTful APIs"]
    },
    "design": {
        "title": "UI/UX & Design Systems",
        "icon": "figma",
        "skills": ["Figma", "UI Design", "UX Research", "Wireframing", "Interactive Prototyping", "Design Systems", "Adobe Photoshop", "Lightroom"]
    },
    "databases": {
        "title": "Databases & Storage",
        "icon": "database",
        "skills": ["PostgreSQL", "SQLite", "Oracle SQL / PL-SQL"]
    },
    "devops_tools": {
        "title": "DevOps & Developer Tools",
        "icon": "terminal",
        "skills": ["Git", "GitHub", "Docker", "CI/CD Pipelines", "Jenkins", "AWS EC2", "Netlify", "Vercel"]
    }
}

# Google Drive Certificate Archive Link
CERTIFICATES_DRIVE_LINK = "https://drive.google.com/drive/folders/1CFHkPI88lUc2VL5dO8tsH-Qf7kNLfTF2?usp=drive_link"

# Authentic certifications
CERTIFICATIONS_DATA = [
    {
        "title": "DevOps Course Certification",
        "issuer": "Tutedude",
        "date": "October 2025",
        "badge": "DevOps & Cloud",
        "desc": "Comprehensive training covering CI/CD pipelines, Docker containerization, Jenkins automation, and cloud deployments.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    },
    {
        "title": "UI/UX Design Certification",
        "issuer": "Tutedude",
        "date": "September 2024",
        "badge": "Design & UI/UX",
        "desc": "Hands-on certification in design systems, user flows, wireframing, high-fidelity UI layout, and interactive Figma prototyping.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    },
    {
        "title": "Data Analytics Essentials",
        "issuer": "Cisco Networking Academy",
        "date": "July 26, 2024",
        "badge": "Data Analytics",
        "desc": "Foundational certification in data analysis methodologies, statistical interpretation, data quality, and analytical problem solving.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    },
    {
        "title": "Web Development Internship",
        "issuer": "Teachnook / Immensphere",
        "date": "September 23, 2022",
        "badge": "Full Stack",
        "desc": "Practical web development internship building interactive frontends, backend APIs, and responsive web applications.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    },
    {
        "title": "Web Development Course",
        "issuer": "Teachnook",
        "date": "September 23, 2022",
        "badge": "Web Engineering",
        "desc": "Training in modern web architectures, semantic HTML5, CSS layout systems, and JavaScript client logic.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    },
    {
        "title": "Build a Full Website Using WordPress",
        "issuer": "Coursera",
        "date": "December 20, 2023",
        "badge": "CMS & Web",
        "desc": "Hands-on guided project building custom website architecture, theme customization, and content management structures.",
        "drive_link": CERTIFICATES_DRIVE_LINK
    }
]

@app.route("/")
def index():
    return render_template("index.html", active_page="home")

@app.route("/projects")
def projects():
    categories = [
        {"name": "All Work", "slug": "all"},
        {"name": "UI/UX Design", "slug": "uiux"},
        {"name": "Full Stack", "slug": "fullstack"},
        {"name": "Web Apps", "slug": "webapp"},
        {"name": "AI & Data", "slug": "aidata"}
    ]
    return render_template("projects.html", projects=PROJECTS_DATA, categories=categories, active_page="projects")

@app.route("/skills")
def skills():
    # Also provide a flattened list for backwards compatibility
    flat_skills = []
    for cat in SKILLS_DATA.values():
        flat_skills.extend(cat["skills"])
    return render_template("skills.html", skill_categories=SKILLS_DATA, skills=flat_skills, active_page="skills")

@app.route("/certifications")
def certifications():
    return render_template("certifications.html", certifications=CERTIFICATIONS_DATA, drive_link=CERTIFICATES_DRIVE_LINK, active_page="certifications")

@app.route("/certifications/drive")
@app.route("/certifications/explore")
def certifications_drive():
    return redirect(CERTIFICATES_DRIVE_LINK)

@app.route("/contact")
@app.route("/contact me")
def contact():
    return render_template("contact&about me.html", active_page="contact")

@app.route("/download-ui-pdf")
@app.route("/download-pdf")
def download_pdf():
    pdf_path = os.path.join(basedir, "static", "docs", "Portfolio_UI_Traceability_Report.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(basedir, "Portfolio_UI_Traceability_Report.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name="Portfolio_UI_Traceability_Report.pdf")
    return abort(404, description="PDF report not found.")

@app.route("/view-ui-pdf")
def view_pdf():
    pdf_path = os.path.join(basedir, "static", "docs", "Portfolio_UI_Traceability_Report.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(basedir, "Portfolio_UI_Traceability_Report.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype="application/pdf")
    return abort(404, description="PDF report not found.")

if __name__ == "__main__":
    app.run(debug=True)
