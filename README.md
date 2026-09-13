Video Maker

اسکریپت Python برای تبدیل ویدئو به HLS ("m3u8") و رمزنگاری آن با AES-128 با استفاده از FFmpeg.

اسکریپت فایل "input" را از پوشه "maker" دریافت می‌کند و فایل Playlist، کلید رمزنگاری و Segmentهای HLS را در پوشه "output" ایجاد می‌کند.

پیش‌نیازها

- Python
- FFmpeg
- قرار داشتن FFmpeg در Windows PATH

بررسی نصب:

python --version
ffmpeg -version

اجرای پروژه

ساختار پروژه:
```
project/
├── video_maker.py
└── maker/
    └── input.mp4
```

سپس:
```
python video_maker.py
```

اگر پوشه "output" از قبل وجود داشته باشد، برنامه برای حذف خروجی قبلی تأیید می‌گیرد.

خروجی‌های احتمالی

در صورت موفقیت:
```
output/
├── output.m3u8
├── enc.key
├── segment_000.ts
├── segment_001.ts
├── segment_002.ts
└── ...
```

```
- "output.m3u8": Playlist اصلی HLS
- "enc.key": کلید AES-128
- "segment_*.ts": Segmentهای رمزنگاری‌شده ویدئو
```
فایل "key_info.txt" فقط موقت است و پس از تبدیل حذف می‌شود. این فایل نباید روی هاست آپلود شود.

خطاهای احتمالی

- "No input file was found": فایل "input" داخل "maker" وجود ندارد.
- "Multiple files with the name 'input'": بیش از یک فایل با نام "input" وجود دارد.
- "FFmpeg was not found": FFmpeg نصب نیست یا در PATH قرار نگرفته است.
- "FFmpeg failed during video conversion": عملیات تبدیل توسط FFmpeg با خطا متوقف شده است.
