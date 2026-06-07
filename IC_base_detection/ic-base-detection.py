import cv2
import numpy as np
import math
import os

# Helpers
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_img(path, img):
    cv2.imwrite(path, img)
    print(f"✔ Saved: {path}")

def contour_center(cnt):
    M = cv2.moments(cnt)
    if M["m00"] == 0:
        x, y, w, h = cv2.boundingRect(cnt)
        return (x + w // 2, y + h // 2)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def fitline_angle(cnt):
    if len(cnt) < 2:
        return None
    vx, vy, x, y = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
    vx = float(vx[0])
    vy = float(vy[0])
    angle = math.degrees(math.atan2(vy, vx))
    return angle

def angle_from_vertical(angle):
    if angle is None:
        return None
    a = angle
    while a > 90:
        a -= 180
    while a < -90:
        a += 180
    return abs(90 - abs(a))

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, "ic.png")
out_dir = os.path.join(current_dir, "results")
ensure_dir(out_dir)

# Load image
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"❌ Cannot load image: {img_path}")

orig = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find dark body region
body_mask = cv2.inRange(gray, 0, 210)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_OPEN, kernel, iterations=1)
body_mask = cv2.morphologyEx(body_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
save_img(os.path.join(out_dir, "body_mask.png"), body_mask)

contours, _ = cv2.findContours(body_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if not contours:
    raise RuntimeError("❌ No body contour found")

body_cnt = max(contours, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(body_cnt)

# ROI: body + pin area below
pad_x = int(w * 0.12)
pad_top = int(h * 0.05)
pad_bottom = int(h * 1.10)

rx1 = max(0, x - pad_x)
ry1 = max(0, y - pad_top)
rx2 = min(img.shape[1], x + w + pad_x)
ry2 = min(img.shape[0], y + h + pad_bottom)

roi = orig[ry1:ry2, rx1:rx2].copy()
roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

debug = orig.copy()
cv2.rectangle(debug, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
save_img(os.path.join(out_dir, "roi_box.png"), debug)

# Build pin mask

# First, we make the initial mask
pin_mask = cv2.inRange(roi_gray, 0, 235)
# We will remove the body from this mask
h_roi, w_roi = pin_mask.shape
# Draw a black rectangle on the body
cv2.rectangle(pin_mask, (0, int(h_roi * 0.4)), (w_roi, h_roi), 0, -1)
# Now we remove small noises
kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
pin_mask = cv2.morphologyEx(pin_mask, cv2.MORPH_OPEN, kernel2, iterations=2)

save_img(os.path.join(out_dir, "pin_mask.png"), pin_mask)

# Column projection to locate pin x-regions

# focus on lower part of ROI where pins are
h_roi, w_roi = pin_mask.shape
lower = pin_mask[int(h_roi * 0.25):, :]  # ignore upper body part
col_sum = np.sum(lower > 0, axis=0).astype(np.float32)

# smooth
col_sum_s = cv2.GaussianBlur(col_sum.reshape(1, -1), (1, 41), 0).flatten()

# threshold peaks
thr = 0.30 * np.max(col_sum_s) if np.max(col_sum_s) > 0 else 0
active = col_sum_s > thr

regions = []
start = None
for i, v in enumerate(active):
    if v and start is None:
        start = i
    elif not v and start is not None:
        if i - start > 3:
            regions.append((start, i - 1))
        start = None
if start is not None:
    if len(active) - start > 3:
        regions.append((start, len(active) - 1))

# merge close regions
merged = []
for r in regions:
    if not merged:
        merged.append(list(r))
    else:
        if r[0] - merged[-1][1] <= 10:
            merged[-1][1] = r[1]
        else:
            merged.append(list(r))
regions = [(a, b) for a, b in merged]

print("X-regions:", regions)

# Extract each pin from each x-region
result = roi.copy()
pin_info = []

for idx, (xs, xe) in enumerate(regions, start=1):
    sub = pin_mask[:, xs:xe + 1]
    cnts, _ = cv2.findContours(sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        continue

    # choose the largest contour in that x-region
    cnt = max(cnts, key=cv2.contourArea)

    # shift contour back
    cnt = cnt + np.array([[[xs, 0]]])

    area = cv2.contourArea(cnt)
    if area < 20:
        continue

    cx, cy = contour_center(cnt)
    ang = fitline_angle(cnt)
    tilt = angle_from_vertical(ang)

    x0, y0, w0, h0 = cv2.boundingRect(cnt)

    # draw
    cv2.drawContours(result, [cnt], -1, (0, 0, 255), 2)
    cv2.circle(result, (cx, cy), 4, (255, 0, 0), -1)

    label = f"P{len(pin_info)+1}"
    cv2.putText(result, label, (x0, max(0, y0 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 128, 0), 2, cv2.LINE_AA)

    pin_info.append({
        "index": len(pin_info) + 1,
        "center": (cx, cy),
        "angle": ang,
        "tilt_from_vertical": tilt,
        "area": area,
        "bbox": (x0, y0, w0, h0),
        "contour": cnt
    })

# If some pins missed, try contour-based fallback
if len(pin_info) < 3:
    print("Fallback: contour-based search on lower ROI...")
    lower_mask = pin_mask[int(h_roi * 0.25):, :]
    cnts, _ = cv2.findContours(lower_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a < 20:
            continue
        x0, y0, w0, h0 = cv2.boundingRect(c)
        # shift back to full ROI coords
        c2 = c.copy()
        c2[:, :, 0] += 0
        c2[:, :, 1] += int(h_roi * 0.25)

        # shift contour x, y back later
        candidates.append((a, c2, (x0, y0 + int(h_roi * 0.25), w0, h0)))

    candidates = sorted(candidates, key=lambda t: t[0], reverse=True)

    # keep unique x positions
    used_x = []
    for a, c, bb in candidates:
        x0, y0, w0, h0 = bb
        if any(abs(x0 - ux) < 20 for ux in used_x):
            continue
        used_x.append(x0)
        c = c + np.array([[[0, 0]]])
        # already in lower coords; shift only y
        c[:, :, 1] += 0
        if len(pin_info) < 3:
            cx, cy = contour_center(c)
            ang = fitline_angle(c)
            tilt = angle_from_vertical(ang)
            x1, y1, w1, h1 = cv2.boundingRect(c)
            cv2.drawContours(result, [c], -1, (255, 0, 0), 2)
            cv2.circle(result, (cx, cy), 4, (0, 255, 255), -1)
            pin_info.append({
                "index": len(pin_info) + 1,
                "center": (cx, cy),
                "angle": ang,
                "tilt_from_vertical": tilt,
                "area": a,
                "bbox": (x1, y1, w1, h1),
                "contour": c
            })

# sort pins left-to-right
pin_info = sorted(pin_info, key=lambda p: p["center"][0])

# Measure distances
distances = []
for i in range(len(pin_info) - 1):
    c1 = pin_info[i]["center"]
    c2 = pin_info[i + 1]["center"]
    d = math.dist(c1, c2)
    distances.append(d)

    midx = (c1[0] + c2[0]) // 2
    midy = (c1[1] + c2[1]) // 2
    cv2.line(result, c1, c2, (0, 255, 255), 1)
    cv2.putText(result, f"{d:.1f}px", (midx, midy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 128), 1, cv2.LINE_AA)

# Save results
save_img(os.path.join(out_dir, "result_pins.png"), result)

full = orig.copy()
cv2.rectangle(full, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
# save_img(os.path.join(out_dir, "result_full_roi.png"), full)

# Print summary
print("\n=== PIN SUMMARY ===")
for p in pin_info:
    print(f"Pin {p['index']}: center={p['center']}, angle={p['angle']}, tilt_from_vertical={p['tilt_from_vertical']}, area={p['area']}")

print("\n=== DISTANCES ===")
for i, d in enumerate(distances, start=1):
    print(f"⭕ Distance Pin {i} -> Pin {i+1}: {d:.2f}px")

# Identify bent pin
if pin_info:
    # Bent pin often has largest tilt from vertical
    valid = [p for p in pin_info if p["tilt_from_vertical"] is not None]
    if valid:
        bent = max(valid, key=lambda p: p["tilt_from_vertical"])
        print(f"\n>>> Bent pin likely: Pin {bent['index']} with tilt {bent['tilt_from_vertical']:.2f} deg")