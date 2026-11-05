from pathlib import Path
from io import BytesIO
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/annad./Downloads/AMAkids-launch-an-EdTech-education-center-on-a-proven-international-model.pptx")
OUT = ROOT / "ready-for-develop/assets/downloads/amakids-partnership-overview.pptx"

PINK = "F73588"
PURPLE = "7B35F4"
ORANGE = "FF8A1F"
BLUE = "148FCA"
INK = "17151E"
MUTED = "66616E"
PALE = "F7F5FA"
WHITE = "FFFFFF"
LINE = "E7E2EC"
SOFT_PINK = "FDE8F2"
SOFT_PURPLE = "EEE7FE"
SOFT_ORANGE = "FFF0DF"
SOFT_BLUE = "E8F5FB"


def rgb(value):
    return RGBColor.from_string(value)


def clear_slide(slide):
    tree = slide.shapes._spTree
    for shape in list(slide.shapes):
        tree.remove(shape._element)


def background(slide, color=WHITE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def rect(slide, x, y, w, h, fill, radius=True, line=None, line_width=0.8):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.color.rgb = rgb(line or fill)
    shape.line.width = Pt(line_width)
    return shape


def text(slide, value, x, y, w, h, size=18, color=INK, bold=False,
         font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
         margin=0, fit=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    frame.word_wrap = True
    if fit:
        frame.fit_text(font_family=font, max_size=Pt(size))
    p = frame.paragraphs[0]
    p.alignment = align
    p.space_after = Pt(0)
    run = p.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    return box


def paragraph(frame, value, size=14, color=INK, bold=False, before=0, after=0, bullet=False):
    p = frame.add_paragraph()
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    p.level = 0
    if bullet:
        p.text = "•  " + value
    else:
        p.text = value
    for run in p.runs:
        run.font.name = "Aptos"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
    return p


def title_block(slide, heading, kicker=None, dark=False):
    title_color = WHITE if dark else INK
    muted_color = "D7CFF0" if dark else MUTED
    if kicker:
        text(slide, kicker.upper(), 0.65, 0.34, 5.5, 0.25, 9, PINK, True)
    text(slide, heading, 0.65, 0.63 if kicker else 0.48, 11.9, 0.66, 26, title_color, False)
    rect(slide, 0.65, 1.32, 0.62, 0.055, PINK, False)
    rect(slide, 1.27, 1.32, 0.45, 0.055, PURPLE, False)
    rect(slide, 1.72, 1.32, 0.28, 0.055, ORANGE, False)
    return muted_color


def label(slide, value, x, y, w, fill, color=WHITE):
    shape = rect(slide, x, y, w, 0.32, fill, True)
    shape.adjustments[0] = 0.22
    text(slide, value.upper(), x, y + 0.01, w, 0.29, 8.5, color, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def add_picture_crop(slide, path, x, y, w, h):
    path = str(path)
    with Image.open(path) as im:
        iw, ih = im.size
    frame_ratio = w / h
    image_ratio = iw / ih
    if image_ratio > frame_ratio:
        shown_w = ih * frame_ratio
        crop = (iw - shown_w) / iw / 2
        pic = slide.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w), height=Inches(h))
        pic.crop_left = crop
        pic.crop_right = crop
    else:
        shown_h = iw / frame_ratio
        crop = (ih - shown_h) / ih / 2
        pic = slide.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w), height=Inches(h))
        pic.crop_top = crop
        pic.crop_bottom = crop
    return pic


def add_picture_compatible(slide, path, x, y, width):
    """Add an image, converting formats such as WebP in memory for PowerPoint."""
    path = Path(path)
    if path.suffix.lower() != ".webp":
        return slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(width))
    stream = BytesIO()
    with Image.open(path) as im:
        im.convert("RGBA").save(stream, format="PNG")
    stream.seek(0)
    return slide.shapes.add_picture(stream, Inches(x), Inches(y), width=Inches(width))


def add_picture_contain(slide, source, x, y, w, h, background_color=PALE):
    """Place the full image inside a fixed frame without cropping people or content."""
    rect(slide, x, y, w, h, background_color, True, background_color)
    if isinstance(source, (bytes, bytearray)):
        stream = BytesIO(source)
        with Image.open(stream) as im:
            iw, ih = im.size
        stream.seek(0)
        image_source = stream
    else:
        image_source = str(source)
        with Image.open(image_source) as im:
            iw, ih = im.size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    return slide.shapes.add_picture(image_source, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), width=Inches(pw), height=Inches(ph))


def top_accent_and_number(slide, number):
    rect(slide, 0, 0, 0.46, 0.055, PINK, False)
    rect(slide, 0.46, 0, 0.34, 0.055, PURPLE, False)
    rect(slide, 0.80, 0, 0.22, 0.055, ORANGE, False)
    rect(slide, 0, 7.43, 7.45, 0.07, PINK, False)
    rect(slide, 7.45, 7.43, 2.35, 0.07, PURPLE, False)
    rect(slide, 9.80, 7.43, 1.70, 0.07, ORANGE, False)
    rect(slide, 11.50, 7.43, 1.83, 0.07, BLUE, False)
    text(slide, f"{number:02d}", 12.28, 7.08, 0.52, 0.20, 8, "A79FB1", True, align=PP_ALIGN.RIGHT)


def fit_legacy_content_to_safe_area(slide, slide_height):
    """Keep inherited shapes above the shared footer instead of letting them drift off-slide."""
    safe_bottom = slide_height - Inches(0.10)
    for shape in slide.shapes:
        bottom = shape.top + shape.height
        if bottom <= safe_bottom:
            continue
        overflow = bottom - safe_bottom
        if shape.height > Inches(0.40):
            shape.height = max(Inches(0.20), shape.height - overflow)
        else:
            shape.top = max(0, shape.top - overflow)


def rebuild_slide_9(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "One digital ecosystem for learning and operations", "Platform + CRM")
    text(slide, "Engage students between lessons and keep the center’s daily work organized in the same AMAkids ecosystem.", 0.65, 1.50, 11.8, 0.38, 13, MUTED)

    platform = ROOT / "ready-for-develop/assets/images/franchise/posters/covers/platform.jpg"
    crm = ROOT / "crm-production/raw/sanitized/01-dashboard.png"
    add_picture_crop(slide, platform, 0.65, 2.02, 5.86, 2.60)
    add_picture_crop(slide, crm, 6.79, 2.02, 5.89, 2.60)
    label(slide, "For students", 0.92, 2.24, 1.08, PINK)
    label(slide, "For the center", 7.06, 2.24, 1.20, PURPLE)

    text(slide, "Learning platform & mobile app", 0.65, 4.86, 5.72, 0.36, 18, INK, True)
    text(slide, "Games, neurotraining, ratings, medals and online practice help students see progress and stay motivated between lessons.", 0.65, 5.29, 5.66, 0.62, 11, MUTED)
    text(slide, "AMAkids CRM", 6.79, 4.86, 5.72, 0.36, 18, INK, True)
    text(slide, "Manage branches, leads, students, trial lessons, groups, schedules, pricing and performance statistics in one workspace.", 6.79, 5.29, 5.66, 0.62, 11, MUTED)

    rect(slide, 0.65, 6.20, 12.03, 0.61, PALE, True, PALE)
    label(slide, "Ongoing support", 0.90, 6.35, 1.35, BLUE)
    text(slide, "Technical and operational guidance helps the partner set up the tools and use them in daily work within the agreed support scope.", 2.52, 6.36, 9.55, 0.25, 10.2, INK, True)
    top_accent_and_number(slide, 9)


def rebuild_slide_10(slide):
    picture_blobs = [shape.image.blob for shape in slide.shapes if shape.shape_type == 13]
    hero_blob = max(picture_blobs, key=len) if picture_blobs else None
    clear_slide(slide)
    background(slide)
    title_block(slide, "Everything a trainer needs for every lesson", "Teaching toolkit")
    text(slide, "A prepared teaching package reduces lesson-planning time and helps teams deliver the selected program consistently.", 0.65, 1.50, 11.8, 0.38, 13, MUTED)

    if hero_blob:
        add_picture_contain(slide, hero_blob, 0.65, 2.02, 5.20, 4.65, WHITE)
    else:
        add_picture_crop(slide, ROOT / "ready-for-develop/assets/images/franchise/courses/mentalnaya-arifmetika.webp", 0.65, 2.02, 5.20, 4.65)
    label(slide, "Ready to use", 0.92, 2.28, 1.08, PINK)

    cards = [
        ("Lesson structure", "Step-by-step plans, presentations and trainer guidance for each stage of the course.", PINK, SOFT_PINK),
        ("Student materials", "Printed workbooks, textbooks, web books and abacuses, depending on the program.", PURPLE, SOFT_PURPLE),
        ("Digital practice", "Platform activities, educational games, homework and progress tools between lessons.", ORANGE, SOFT_ORANGE),
        ("Interactive formats", "Augmented-reality materials and visual demonstrations that make practice more engaging.", BLUE, SOFT_BLUE),
    ]
    for i, (heading, body, accent, soft) in enumerate(cards):
        x = 6.15 + (i % 2) * 3.24
        y = 2.02 + (i // 2) * 2.18
        rect(slide, x, y, 2.97, 1.92, soft, True, soft)
        rect(slide, x + 0.22, y + 0.24, 0.42, 0.42, accent, True, accent)
        text(slide, f"{i+1:02d}", x + 0.22, y + 0.27, 0.42, 0.25, 9, WHITE, True, align=PP_ALIGN.CENTER)
        text(slide, heading, x + 0.22, y + 0.81, 2.50, 0.30, 14, INK, True)
        text(slide, body, x + 0.22, y + 1.18, 2.50, 0.55, 9.7, MUTED)

    text(slide, "Materials and formats vary by selected program and market.", 6.15, 6.54, 6.20, 0.22, 9, MUTED, False, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 10)


def rebuild_slide_11(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "Commercial terms by partnership model", "Contracts, territory & royalty")
    text(slide, "The formats differ in legal scope, territory and the partner’s development responsibility.", 0.65, 1.48, 11.8, 0.42, 13, MUTED)

    left = 2.42
    col_w = 3.42
    headers = [
        ("Single-Unit", PINK),
        ("School Partnership", PURPLE),
        ("Master Franchise", ORANGE),
    ]
    text(slide, "TERM", 0.72, 2.13, 1.42, 0.25, 9, MUTED, True)
    for i, (heading, accent) in enumerate(headers):
        x = left + i * col_w
        rect(slide, x, 1.98, col_w - 0.13, 0.60, accent, True, accent)
        text(slide, heading, x + 0.16, 2.12, col_w - 0.45, 0.28, 13, WHITE, True, align=PP_ALIGN.CENTER)

    rows = [
        ("Agreement", 1.12, [
            "International Commercial Concession Agreement",
            "License Agreement",
            "International Commercial Concession Agreement with sub-licensing rights",
        ]),
        ("Standard monthly royalty", 0.76, ["10%", "10%", "5%"]),
        ("Territory & exclusivity", 1.14, [
            "One or more centers within a limited territory, usually a city",
            "Program licensed to a specific educational institution",
            "Exclusive development rights for an agreed country or region",
        ]),
        ("Partner’s main objective", 1.22, [
            "Build brand awareness and develop the center consistently",
            "Maintain a stable flow of students for the licensed program",
            "Represent the brand regionally and drive network expansion",
        ]),
    ]
    y = 2.76
    softs = [SOFT_PINK, SOFT_PURPLE, SOFT_ORANGE]
    for row_index, (row_name, row_h, values) in enumerate(rows):
        rect(slide, 0.65, y, 1.64, row_h - 0.08, PALE, True, PALE)
        text(slide, row_name, 0.83, y + 0.17, 1.29, row_h - 0.30, 10.5, INK, True, valign=MSO_ANCHOR.MIDDLE)
        for i, value in enumerate(values):
            x = left + i * col_w
            rect(slide, x, y, col_w - 0.13, row_h - 0.08, softs[i], True, softs[i])
            size = 17 if row_index == 1 else 10.2
            text(slide, value, x + 0.20, y + 0.13, col_w - 0.53, row_h - 0.29, size, INK, row_index == 1, valign=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        y += row_h

    rect(slide, 0.65, 6.77, 12.03, 0.40, PALE, True, PALE)
    text(slide, "Commercial terms and territory definitions are reflected in the final individual offer and signed agreement.", 0.92, 6.87, 11.50, 0.18, 9.4, MUTED, False, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 11)


def rebuild_slide_13(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "How a center builds toward profitability", "Economics")
    text(slide, "Profitability is the outcome of a connected operating system—not one headline metric.", 0.65, 1.50, 11.6, 0.38, 13, MUTED)

    steps = [
        ("01", "Attract", "Reach the right local families", PINK, SOFT_PINK),
        ("02", "Convert", "Turn enquiries and trials into enrollments", PURPLE, SOFT_PURPLE),
        ("03", "Fill groups", "Use classroom and trainer capacity well", ORANGE, SOFT_ORANGE),
        ("04", "Retain", "Deliver value and support re-enrollment", BLUE, SOFT_BLUE),
        ("05", "Scale", "Open new groups when demand supports them", PINK, SOFT_PINK),
    ]
    for i, (num, heading, body, accent, soft) in enumerate(steps):
        x = 0.65 + i * 2.46
        rect(slide, x, 2.06, 2.12, 2.18, WHITE, True, LINE)
        rect(slide, x + 0.18, 2.27, 0.48, 0.48, accent, True, accent)
        text(slide, num, x + 0.18, 2.30, 0.48, 0.30, 10, WHITE, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        text(slide, heading, x + 0.18, 2.92, 1.75, 0.32, 16, INK, True)
        text(slide, body, x + 0.18, 3.34, 1.72, 0.65, 10.5, MUTED)
        if i < 4:
            text(slide, "→", x + 2.15, 2.93, 0.30, 0.30, 17, "BDB5C5", True, align=PP_ALIGN.CENTER)

    rect(slide, 0.65, 4.62, 5.85, 1.62, SOFT_PURPLE, True, SOFT_PURPLE)
    label(slide, "Revenue engine", 0.92, 4.88, 1.44, PURPLE)
    text(slide, "Active students  ×  realized monthly price", 0.92, 5.42, 5.08, 0.42, 18, INK, True)
    text(slide, "Enrollment, group occupancy and retention determine how much capacity becomes revenue.", 0.92, 5.88, 5.10, 0.30, 10, MUTED)

    rect(slide, 6.76, 4.62, 5.92, 1.62, SOFT_ORANGE, True, SOFT_ORANGE)
    label(slide, "Cost discipline", 7.03, 4.88, 1.42, ORANGE)
    text(slide, "Acquisition + team + space + operations", 7.03, 5.42, 5.15, 0.42, 18, INK, True)
    text(slide, "Costs must match the center’s stage, local price level and realistic enrollment plan.", 7.03, 5.88, 5.12, 0.30, 10, MUTED)

    text(slide, "The model should be stress-tested for your city, tax environment and chosen format.", 0.65, 6.56, 12.0, 0.26, 10, MUTED, False, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 13)


def rebuild_slide_14(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "Build the financial model around your market", "Individual planning")
    text(slide, "There is no universal investment, margin or payback figure. Start with the inputs you can validate.", 0.65, 1.50, 11.8, 0.38, 13, MUTED)

    inputs = [
        ("01", "Market & pricing", "Demand, competitors, local tuition range and discount policy", PINK, SOFT_PINK),
        ("02", "Model & programs", "Single-Unit, School Partnership or Master Franchise; selected course portfolio", PURPLE, SOFT_PURPLE),
        ("03", "Existing resources", "Premises, audience, equipment and team you already have", ORANGE, SOFT_ORANGE),
        ("04", "Local cost base", "Rent, fit-out, salaries, taxes, registration and launch promotion", BLUE, SOFT_BLUE),
    ]
    for i, (num, heading, body, accent, soft) in enumerate(inputs):
        x = 0.65 + (i % 2) * 3.18
        y = 2.08 + (i // 2) * 1.72
        rect(slide, x, y, 2.92, 1.44, soft, True, soft)
        text(slide, num, x + 0.18, y + 0.17, 0.38, 0.26, 9, accent, True)
        text(slide, heading, x + 0.18, y + 0.45, 2.52, 0.30, 14, INK, True)
        text(slide, body, x + 0.18, y + 0.82, 2.52, 0.48, 9.7, MUTED)

    rect(slide, 7.15, 2.08, 5.53, 3.98, PURPLE, True, PURPLE)
    label(slide, "Your tailored scenario", 7.46, 2.38, 1.78, PINK)
    text(slide, "A decision tool—not a promise", 7.46, 2.91, 4.55, 0.42, 20, WHITE, True)
    outputs = [
        "One-time opening costs and initial AMAkids payment",
        "Monthly operating plan and working-capital need",
        "Enrollment, pricing and group-capacity assumptions",
        "Sensitivity: what changes if launch is slower or costs are higher",
    ]
    for j, item in enumerate(outputs):
        rect(slide, 7.48, 3.55 + j * 0.55, 0.18, 0.18, WHITE, True, WHITE)
        text(slide, "✓", 7.49, 3.51 + j * 0.55, 0.16, 0.22, 10, PURPLE, True, align=PP_ALIGN.CENTER)
        text(slide, item, 7.78, 3.48 + j * 0.55, 4.18, 0.40, 10.5, WHITE)

    rect(slide, 0.65, 6.38, 12.03, 0.53, PALE, True, PALE)
    text(slide, "AMAkids can discuss an individual estimate after reviewing your country, format, resources and development plan.", 0.90, 6.53, 11.55, 0.22, 10.5, INK, True, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 14)


def rebuild_slide_15(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "Validate the assumptions before you invest", "Due diligence")
    text(slide, "The strongest plan replaces generic benchmarks with evidence from your city and operating format.", 0.65, 1.50, 11.8, 0.38, 13, MUTED)

    items = [
        ("Demand", "Who is the target family? What alternatives exist? What price range is realistic?", PINK, SOFT_PINK),
        ("Space", "What do local rules require? How many groups can the premises support?", PURPLE, SOFT_PURPLE),
        ("Team", "Who will teach and manage? What is the recruitment and preparation timeline?", ORANGE, SOFT_ORANGE),
        ("Acquisition", "Which local channels will generate enquiries and trial lessons—and at what cost?", BLUE, SOFT_BLUE),
        ("Retention", "How will the calendar, parent communication and re-enrollment process work?", PINK, SOFT_PINK),
        ("Cash", "What working-capital reserve, tax allowance and contingency are needed?", PURPLE, SOFT_PURPLE),
    ]
    for i, (heading, body, accent, soft) in enumerate(items):
        x = 0.65 + (i % 3) * 4.16
        y = 2.08 + (i // 3) * 1.78
        rect(slide, x, y, 3.82, 1.48, WHITE, True, LINE)
        rect(slide, x, y, 0.11, 1.48, accent, False, accent)
        text(slide, heading, x + 0.27, y + 0.20, 3.25, 0.30, 15, INK, True)
        text(slide, body, x + 0.27, y + 0.61, 3.23, 0.65, 10.2, MUTED)

    rect(slide, 0.65, 5.96, 12.03, 0.76, PALE, True, PALE)
    label(slide, "First-call checklist", 0.92, 6.18, 1.46, PINK)
    text(slide, "Country & city  ·  preferred model  ·  existing school/resources  ·  programs of interest  ·  target timing", 2.64, 6.22, 9.50, 0.24, 10.5, INK, True)
    top_accent_and_number(slide, 15)


def rebuild_slide_17(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "What an AMAkids center can look like", "Learning environment")
    text(slide, "A bright, welcoming space for small-group learning—adapted to the premises, local regulations and chosen programs.", 0.65, 1.50, 11.9, 0.38, 13, MUTED)

    img1 = Path("/Users/annad./Desktop/468157543_122185311248088138_6790389826477769828_n.jpg")
    img2 = Path("/Users/annad./Desktop/468331794_122185310846088138_5587917687720042299_n.jpg")
    img3 = Path("/Users/annad./Desktop/489289964_122196198524094453_8141149851796277381_n.jpg")
    add_picture_crop(slide, img1, 0.65, 2.04, 7.62, 4.27)
    rect(slide, 0.82, 5.76, 2.33, 0.37, INK, True, INK)
    text(slide, "EXISTING AMAKIDS CENTER", 0.92, 5.84, 2.12, 0.18, 8, WHITE, True, align=PP_ALIGN.CENTER)
    add_picture_crop(slide, img2, 8.53, 2.04, 4.15, 1.93)
    add_picture_crop(slide, img3, 8.53, 4.22, 4.15, 2.09)
    label(slide, "Design concept", 8.75, 3.49, 1.28, ORANGE)
    label(slide, "Classroom in use", 8.75, 5.83, 1.36, BLUE)

    rect(slide, 0.65, 6.52, 12.03, 0.40, PALE, True, PALE)
    text(slide, "Brand identity  ·  classroom technology  ·  teaching tools  ·  flexible small-group layout", 0.90, 6.62, 11.55, 0.18, 10, INK, True, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 17)


def rebuild_slide_18(slide):
    clear_slide(slide)
    background(slide)
    title_block(slide, "Events that make progress visible", "Community & motivation")
    text(slide, "From local Olympiads to international stages, students get goals to work toward and moments worth celebrating.", 0.65, 1.50, 11.8, 0.38, 13, MUTED)

    world = ROOT / "ready-for-develop/assets/images/franchise/events/world-cup-2024.jpg"
    event1 = Path("/Users/annad./Desktop/Знімок екрана 2026-11-04 о 18.27.54.png")
    event2 = Path("/Users/annad./Desktop/Знімок екрана 2026-11-04 о 18.36.23.png")
    logo = Path("/Users/annad./Desktop/Marketing/VFCupLogo/VFCupLogo.png")

    # The hero keeps the children intact; only a small portion of the ceiling is cropped.
    hero = slide.shapes.add_picture(str(world), Inches(0.65), Inches(2.02), width=Inches(7.20), height=Inches(3.54))
    hero.crop_top = 0.13
    hero.crop_bottom = 0.01
    add_picture_contain(slide, event1, 0.65, 5.78, 3.45, 1.13, SOFT_PINK)
    add_picture_contain(slide, event2, 4.40, 5.78, 3.45, 1.13, SOFT_BLUE)
    rect(slide, 8.13, 2.02, 4.55, 4.89, SOFT_PURPLE, True, SOFT_PURPLE)
    slide.shapes.add_picture(str(logo), Inches(9.12), Inches(2.23), width=Inches(2.55))
    text(slide, "Regular event formats", 8.53, 3.78, 3.75, 0.34, 16, INK, True, align=PP_ALIGN.CENTER)
    formats = [
        "Local Olympiads organized by AMAkids partners",
        "Large international Olympiads and community events",
        "Annual international online tournament",
        "Mental-arithmetic battle for students",
    ]
    for j, item in enumerate(formats):
        rect(slide, 8.52, 4.35 + j * 0.51, 0.17, 0.17, PINK, True, PINK)
        text(slide, item, 8.82, 4.28 + j * 0.51, 3.34, 0.36, 10.2, INK)
    text(slide, "Events may vary by market and season.", 8.53, 6.57, 3.75, 0.20, 8.5, MUTED, False, align=PP_ALIGN.CENTER)
    top_accent_and_number(slide, 18)


def rebuild_slide_19(slide):
    clear_slide(slide)
    background(slide)
    logo = ROOT / "ready-for-develop/assets/images/brand/logo-header.webp"
    add_picture_compatible(slide, logo, 0.68, 0.48, 1.78)
    rect(slide, 0, 0, 13.33, 0.08, PINK, False)
    rect(slide, 0.42, 1.22, 7.00, 5.40, SOFT_BLUE, True, SOFT_BLUE)
    rect(slide, 0.42, 1.22, 0.13, 5.40, BLUE, False, BLUE)
    text(slide, "Ready to explore AMAkids in your market?", 0.78, 1.58, 6.25, 1.05, 29, INK, True)
    text(slide, "Book a conversation with the international development team and receive a proposal shaped around your country, format and resources.", 0.78, 2.79, 6.05, 0.78, 13, MUTED)

    label(slide, "Bring to the first call", 0.68, 3.82, 1.63, PINK)
    items = ["Country and city", "Preferred partnership model", "Existing school, premises or team", "Programs and target launch timing"]
    for j, item in enumerate(items):
        rect(slide, 0.72, 4.39 + j * 0.46, 0.17, 0.17, ORANGE, True, ORANGE)
        text(slide, item, 1.02, 4.31 + j * 0.46, 5.65, 0.34, 11.5, INK)

    rect(slide, 7.75, 0.65, 4.93, 6.18, SOFT_PURPLE, True, SOFT_PURPLE)
    label(slide, "Contact", 8.38, 1.05, 0.88, PURPLE)
    text(slide, "Let’s discuss your city", 8.38, 1.58, 3.82, 0.48, 21, INK, True)
    text(slide, "Email", 8.38, 2.45, 3.65, 0.22, 9, MUTED, True)
    text(slide, "international@amakids.com", 8.38, 2.76, 3.72, 0.36, 14, PURPLE, True)
    rect(slide, 8.38, 3.31, 3.90, 0.012, WHITE, False, WHITE)
    text(slide, "WhatsApp / Telegram", 8.38, 3.64, 3.65, 0.22, 9, MUTED, True)
    text(slide, "+357 94 086346", 8.38, 3.95, 3.72, 0.36, 18, PINK, True)
    rect(slide, 8.38, 4.58, 3.90, 1.42, WHITE, True, WHITE)
    text(slide, "What you’ll get", 8.65, 4.83, 3.34, 0.28, 11, INK, True)
    text(slide, "A fit check, practical launch path and an individual financial discussion for your proposed format.", 8.65, 5.20, 3.16, 0.60, 10.3, MUTED)

    text(slide, "amakids.com", 0.68, 7.02, 2.0, 0.20, 9, MUTED, True)
    top_accent_and_number(slide, 19)


def replace_exact_text(slide, old, new):
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph_item in shape.text_frame.paragraphs:
            full = "".join(run.text for run in paragraph_item.runs)
            if old in full:
                for run in paragraph_item.runs:
                    if old in run.text:
                        run.text = run.text.replace(old, new)
                        return True
                paragraph_item.text = full.replace(old, new)
                return True
    return False


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation(SOURCE)

    # Add a restrained brand accent and slide number to the preserved slides.
    replaced = {9, 10, 11, 13, 17, 18, 19}
    for number, slide in enumerate(prs.slides, 1):
        if number not in replaced:
            fit_legacy_content_to_safe_area(slide, prs.slide_height)
            top_accent_and_number(slide, number)

    rebuild_slide_9(prs.slides[8])
    rebuild_slide_10(prs.slides[9])
    rebuild_slide_11(prs.slides[10])
    rebuild_slide_13(prs.slides[12])
    rebuild_slide_17(prs.slides[16])
    rebuild_slide_18(prs.slides[17])
    rebuild_slide_19(prs.slides[18])

    label(prs.slides[13], "Planning example · not a forecast", 9.72, 0.52, 2.60, PURPLE)
    label(prs.slides[14], "Illustrative benchmarks · validate locally", 9.44, 0.52, 2.88, PINK)

    # Align the launch promise with the current website handoff copy.
    replace_exact_text(prs.slides[0], "AMAkids: launch an EdTech education center on a proven international model", "AMAkids: open an education center with a proven international EdTech model")
    replace_exact_text(prs.slides[1], "Launch assistance and full-path support: technical and operational.", "Launch guidance and ongoing technical and operational support within the agreed partnership scope.")
    replace_exact_text(prs.slides[3], "Three programs fully adapted for English-language markets, for ages 5–16. Take the full package or choose individual programs.", "The current English-language offer includes three programs for children and teens. Take the full package or choose individual programs.")
    replace_exact_text(prs.slides[4], "Build fast perception and information processing through mental counting.", "Use abacus-based and mental calculation exercises to develop children’s learning skills.")
    replace_exact_text(prs.slides[7], "Results from the first lessons", "Progress from the first lessons")
    replace_exact_text(prs.slides[7], "Visible results within a month, and increasingly advanced skills as students progress.", "Progress is made visible from the first lessons, with increasingly advanced skills as students continue.")
    replace_exact_text(prs.slides[7], "Teacher training and certification", "Teacher preparation and training")
    replace_exact_text(prs.slides[7], "A clear training system and structured methodological materials for teachers.", "Course-specific training and structured methodological materials prepare teachers to deliver the selected programs.")
    replace_exact_text(prs.slides[8], "Our own platform, CRM and full tech support", "Our own platform, CRM and ongoing tech support")
    replace_exact_text(prs.slides[8], "Full tech support", "Ongoing technical support")
    replace_exact_text(prs.slides[8], "Launch assistance and technical and operational support at every step.", "Launch guidance and ongoing technical and operational support within the agreed scope.")
    replace_exact_text(prs.slides[11], "Franchise or territory fee", "Initial AMAkids payment")
    replace_exact_text(prs.slides[15], "Average launch time · 60–90 days", "Typical preparation · around 3–6 months")
    replace_exact_text(prs.slides[15], "Sign and secure the territory.", "Confirm the model and available territory.")
    replace_exact_text(prs.slides[15], "Partner training and trainer certification.", "Partner training and course-specific trainer preparation.")

    prs.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
