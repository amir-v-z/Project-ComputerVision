## 🏗 ساختار پروژه

```
IC_base_detection/
│
├── results/                 # این پوشه پس از اجرا ساخته میشود
│   ├── body_mask.png
│   ├── pin_mask.png
│   ├── result_pins.png
│   └── roi_box.png
│
├── ic_base_detection.py     # فایل اصلی برنامه
├── ic.png                   # تصویر آی سی
├── README.md
└── requirements.txt         # وابستگی های لازم
```

# 📝 نحوه اجرا

### 1. دانلود پوشه `IC_base_detection`

### 2. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 3. فایل `ic_base_detection.py` را اجرا کنید.

```bash
python ic_base_detection.py
```