import cv2
import numpy as np
import math
import os

# ==========================================
# PARAMETERS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISC_IMAGE = os.path.join(BASE_DIR, "img", "disc.jpg")

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# اندازه های واقعی اعلام شده
NOMINAL_CENTER_DIAMETER = 75.0      # mm - قطر سوراخ مرکزی
NOMINAL_OUTER_DIAMETER = 240.0      # mm - قطر بیرونی دیسک
NOMINAL_HOLE_DIAMETER = 10.0        # mm - قطر سوراخ های پیچ
NOMINAL_CROSS_DISTANCE = 93.0       # mm - فاصله ضربدری سوراخ ها

# ==========================================
# UTILITIES
# ==========================================

def distance(p1, p2):

    dx = float(p1[0]) - float(p2[0])
    dy = float(p1[1]) - float(p2[1])

    return np.sqrt(dx*dx + dy*dy)

def mm_round(x):
    return round(x, 1)

def circularity(cnt):
    area = cv2.contourArea(cnt)

    if area <= 0:
        return 0

    peri = cv2.arcLength(cnt, True)

    if peri <= 0:
        return 0

    return 4.0 * np.pi * area / (peri * peri)

# ==========================================
# LOAD IMAGE
# ==========================================

img = cv2.imread(DISC_IMAGE)

if img is None:
    raise Exception("disc.jpg not found")

original = img.copy()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

gray = cv2.GaussianBlur(gray, (7,7), 1)

# ==========================================
# CENTRAL HOLE DETECTION (LOCAL ROI)
# ==========================================

h, w = gray.shape

# یک ROI تقریبی از مرکز تصویر
# این ROI فقط برای پیدا کردن سوراخ سفید وسط است
roi_x1 = 60
roi_y1 = 60
roi_x2 = 420
roi_y2 = 420

center_roi = gray[roi_y1:roi_y2, roi_x1:roi_x2]

circles = cv2.HoughCircles(
    center_roi,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=80,
    param1=100,
    param2=20,
    minRadius=100,
    maxRadius=180
)

if circles is None:
    raise Exception("Central hole not detected")

circles = np.uint16(np.around(circles))

c = circles[0][0]
cx = int(c[0] + roi_x1)
cy = int(c[1] + roi_y1)
r_center = int(c[2])

print("Central hole (px):", cx, cy, r_center)

# ==========================================
# HOLE DETECTION USING CONTOURS
# ==========================================

_, thresh = cv2.threshold(
    gray,
    180,
    255,
    cv2.THRESH_BINARY
)

kernel = np.ones((3,3), np.uint8)

thresh = cv2.morphologyEx(
    thresh,
    cv2.MORPH_OPEN,
    kernel
)

contours, _ = cv2.findContours(
    thresh,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

print("Contours found =", len(contours))

candidates = []

for cnt in contours:
    
    area = cv2.contourArea(cnt)

    if area < 700:
        continue

    if area > 2000:
        continue

    circ = circularity(cnt)

    if circ < 0.75:
        continue

    (x, y), radius = cv2.minEnclosingCircle(cnt)

    x = int(x)
    y = int(y)

    dist_from_center = distance(
        (x, y),
        (cx, cy)
    )

    candidates.append(
        (
            x,
            y,
            radius,
            dist_from_center
        )
    )

# استفاده مستقیم از سوراخ های کاندید
holes = candidates

print("Candidates =", len(holes))

if len(candidates) != 4:
    raise Exception(f"Expected exactly 4 holes, but detected {len(candidates)}")

# مرتب سازی زاویه ای
angles = []

for h in holes:

    angle = math.atan2(
        float(h[1]) - float(cy),
        float(h[0]) - float(cx)
    )

    angles.append((angle, h))

angles.sort()

holes = [x[1] for x in angles]

# ==========================================
# Refined bolt-circle center
# ==========================================

bolt_cx = np.mean([h[0] for h in holes])
bolt_cy = np.mean([h[1] for h in holes])

print("Bolt circle center =", round(bolt_cx, 2), round(bolt_cy, 2))

# ==========================================
# POLISHED REGION (ANNULAR SURFACE)
# ==========================================

mask_outer = np.zeros(gray.shape, dtype=np.uint8)

outer = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=300,
    param1=120,
    param2=60,
    minRadius=320,
    maxRadius=420
)

if outer is None:
    raise Exception("Outer disc not detected")

outer = np.uint16(np.around(outer))

ox, oy, outer_circle_radius = outer[0][0]

# دایره آبی
outer_radius = int(outer_circle_radius)

center_diameter_px = 2.0 * r_center

outer_diameter_px = 2.0 * outer_radius

mm_per_pixel = (NOMINAL_OUTER_DIAMETER / outer_diameter_px)

print("Calibration reference: outer disc")

print(
    "Outer diameter (px):",
    mm_round(outer_diameter_px)
)

print(
    "Scale:",
    round(mm_per_pixel, 4),
    "mm/pixel"
)

# ==========================================
# POLISHED REGION MASK - OUTER ANNULAR SURFACE ONLY
# ==========================================

# مرز داخلی سطح صیقلی
INNER_POLISHED_RATIO = 0.66

inner_polished_radius = int(outer_radius * INNER_POLISHED_RATIO)

# مرکز حلقه داخلی را با مرکز دایره بیرونی یکسان می‌گیریم
# تا ماسک حلقوی جابه‌جا نشود
ix, iy = int(ox), int(oy)

mask_outer = np.zeros(gray.shape, dtype=np.uint8)
mask_inner = np.zeros(gray.shape, dtype=np.uint8)

# کل ناحیه داخل لبه بیرونی دیسک
cv2.circle(
    mask_outer,
    (int(ox), int(oy)),
    outer_radius,
    255,
    -1
)

# حذف کامل بخش مرکزی دیسک؛ فقط حلقه بیرونی باقی می‌ماند
cv2.circle(
    mask_inner,
    (int(ox), int(oy)),
    inner_polished_radius,
    255,
    -1
)

polished_mask = cv2.subtract(mask_outer, mask_inner)

# حاشیه اطمینان اطراف چهار سوراخ نیز از ماسک حذف می‌شود
for h in holes:
    x, y, r, _ = h
    cv2.circle(polished_mask, (x, y), int(r * 2.8), 0, -1)

# ==========================================
# AREA DEFECT DETECTION
# ==========================================

# ROI فقط برای ذخیره و نمایش
roi = cv2.bitwise_and(gray, gray, mask=polished_mask)

# بلور را روی تصویر خاکستری کامل بزن، نه روی ROI صفرشده
bg = cv2.medianBlur(gray, 15)

# چون دنبال لکه‌های تیره هستیم:
# جاهایی که از زمینه محلی تیره‌ترند را حساب می‌کنیم
dark_diff = cv2.subtract(bg, gray)

# فقط داخل ناحیه صیقلی نگه دار
dark_diff = cv2.bitwise_and(dark_diff, dark_diff, mask=polished_mask)

# آستانه پایین‌تر برای دیدن لکه‌های سیاه
_, defect_mask = cv2.threshold(
    dark_diff,
    18,   # بین 12 تا 25 تست کن
    255,
    cv2.THRESH_BINARY
)

# حذف نویزهای خیلی ریز
defect_mask = cv2.morphologyEx(
    defect_mask,
    cv2.MORPH_OPEN,
    np.ones((3,3), np.uint8)
)

# یکی کردن پیکسل‌های نزدیک به هم
defect_mask = cv2.morphologyEx(
    defect_mask,
    cv2.MORPH_CLOSE,
    np.ones((5,5), np.uint8)
)

# فقط داخل ماسک باقی بماند
defect_mask = cv2.bitwise_and(defect_mask, defect_mask, mask=polished_mask)

num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(defect_mask)

defects = []
defect_boxes = []

for i in range(1, num_labels):

    area_px = stats[i, cv2.CC_STAT_AREA]

    if area_px > 15:

        area_mm2 = area_px * (mm_per_pixel**2)

        defects.append(area_mm2)

        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        defect_boxes.append((x, y, w, h))

# ==========================================
# MEASUREMENTS
# ==========================================

print("\n========== RESULTS ==========\n")

# ===== Centeral Hole =====
print("Central Hole =====")

center_diameter_mm = center_diameter_px * mm_per_pixel
center_deviation = center_diameter_mm - NOMINAL_CENTER_DIAMETER

print("Measured =", mm_round(center_diameter_mm), "mm")
print("Nominal  =", NOMINAL_CENTER_DIAMETER, "mm")
print("Deviation =", mm_round(center_deviation), "mm")

# ===== Bolt Holes =====
print("\nBolt Holes =====")

hole_centers = []

for idx, h in enumerate(holes):

    x,y,r,_ = h

    hole_centers.append((x,y))

    hole_diameter_mm = (2*r) * mm_per_pixel # قطر هر کدام از 4 سوراخ‌ها

    deviation = hole_diameter_mm - NOMINAL_HOLE_DIAMETER

    print(f"Hole {idx+1}")
    print("Measured =", mm_round(hole_diameter_mm), "mm")
    print("Nominal  =", NOMINAL_HOLE_DIAMETER, "mm")
    print("Deviation =", mm_round(deviation), "mm")
    print()

# ===== CROSS DISTANCES =====
print("\nCross Distances =====")

cross_pairs = [(0,2),(1,3)] # فاصله مراکز 4 سوراخ بصورت ضربدری از هم

for a,b in cross_pairs:

    d_px = distance(
        hole_centers[a],
        hole_centers[b]
    )

    d_mm = d_px * mm_per_pixel

    deviation = d_mm - NOMINAL_CROSS_DISTANCE

    print(f"{a+1}-{b+1}")
    print("Measured =", mm_round(d_mm), "mm")
    print("Nominal  =", NOMINAL_CROSS_DISTANCE, "mm")
    print("Deviation =", mm_round(deviation), "mm")
    print()

# ===== BOLT CIRCLE CHECK =====
print("\nBolt Circle Analysis =====")

nominal_radius = NOMINAL_CROSS_DISTANCE / 2.0

radii_mm = []

for h in holes:

    x, y, _, _ = h

    # فاصله هر سوراخ تا مرکز سوراخ مرکزی
    rr = distance((x, y), (cx, cy))

    radii_mm.append(rr * mm_per_pixel)

mean_radius = np.mean(radii_mm)

print("Nominal Radius =", mm_round(nominal_radius), "mm")
print("Mean Measured Radius =", mm_round(mean_radius), "mm")
print()

for i, radius_mm in enumerate(radii_mm):

    nominal_deviation = radius_mm - nominal_radius

    # میزان خارج شدن هر سوراخ از دایره با شعاع ثابت
    fixed_circle_deviation = radius_mm - mean_radius

    print(f"Hole {i+1}")
    print("Measured Radius =", mm_round(radius_mm), "mm")
    print("Nominal Radius  =", mm_round(nominal_radius), "mm")
    print("Deviation from Nominal =", mm_round(nominal_deviation), "mm")
    print("Deviation from Fixed Circle =", mm_round(fixed_circle_deviation), "mm")
    print()

# ==========================================
# DEFECT REPORT
# ==========================================

print("\nSurface Defects =====")
print("Number of defects =", len(defects))

for i,a in enumerate(defects):
    print(f"Defect {i+1} Area =", mm_round(a), "mm²")

# ==========================================
# VISUALIZATION
# ==========================================

vis = original.copy()

for idx, h in enumerate(holes):

    x,y,r,_ = h

    # دایره تشخیص داده‌شده‌ی سوراخ
    cv2.circle(vis, (x,y), int(r), (0,0,255), 2)

    # مرکز سوراخ
    cv2.circle(vis, (x,y), 2, (255,0,0), -1)

    # نمایش شماره سوراخ‌ها
    cv2.putText(
        vis,
        str(idx+1),
        (x+10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0,255,0),
        2
    )

# خط بین مرکز سوراخ مرکزی و مرکز محاسبه‌شده Bolt Circle
cv2.line(
    vis,
    (int(cx), int(cy)),
    (int(round(bolt_cx)), int(round(bolt_cy))),
    (255, 0, 255),
    2
)

# مرکز Bolt Circle محاسبه‌شده از میانگین مراکز چهار سوراخ
cv2.circle(
    vis,
    (int(round(bolt_cx)), int(round(bolt_cy))),
    4,
    (255, 255, 0),
    -1
)

# ==========================================
# Draw detected centers
# ==========================================

# دایره سبز دقیقاً روی سوراخ سفید مرکزی
cv2.circle(vis, (int(cx), int(cy)), int(r_center), (0, 255, 0), 2)

# نقطه سبز در مرکز واقعی سوراخ سفید
cv2.circle(vis, (int(cx), int(cy)), 5, (0, 255, 0), -1)

# مرز خارجی دیسک
cv2.circle(vis, (int(ox), int(oy)), outer_radius, (255,0,0), 2)

# مرز داخلی ناحیه صیقلی
cv2.circle(vis, (int(ix), int(iy)), int(inner_polished_radius), (0,255,0), 2)

# نمایش کادر عیوب
for x, y, box_w, box_h in defect_boxes:
    cv2.rectangle(vis, (x, y), (x + box_w, y + box_h), (0, 0, 255), 2)

offset = distance((cx, cy), (bolt_cx, bolt_cy)) * mm_per_pixel

print("\n=== Center Offset ===")
print("Measured =", mm_round(offset), "mm")
print("Nominal  = 0.0 mm")
print("Deviation =", mm_round(offset), "mm")

cv2.putText(
    vis,
    f"Holes : {len(holes)}",
    (20,30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255,255,255),
    2
)

cv2.putText(
    vis,
    f"Defects : {len(defects)}",
    (20,50),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255,255,255),
    2
)

# Overlay ناحیه صیقلی
overlay = vis.copy()

overlay[polished_mask > 0] = (0,255,255)

cv2.addWeighted(overlay, 0.25, vis, 0.75, 0, vis)

print()
# ذخیره خروجی‌ها
cv2.imwrite(
    os.path.join(OUTPUT_DIR, "polished_mask.jpg"),
    polished_mask
)
print("Saved: polished_mask.jpg")

cv2.imwrite(
    os.path.join(OUTPUT_DIR, "defect_mask.jpg"),
    defect_mask
)
print("Saved: defect_mask.jpg")

cv2.imwrite(
    os.path.join(OUTPUT_DIR, "roi.jpg"),
    roi
)
print("Saved: roi.jpg")

output_file = os.path.join(OUTPUT_DIR, "inspection_result.jpg")
cv2.imwrite(output_file, vis)

print("Saved: inspection_result.jpg")