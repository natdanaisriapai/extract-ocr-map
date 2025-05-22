# Extract-OCR-Map - OCR Data Extraction Pipeline

โปรเจคนี้เป็นระบบสกัดข้อมูลจากเอกสารที่ดิน (OCR) และแปลงเป็นข้อมูล JSON สำหรับการใช้งานต่อ โดยใช้ OpenAI GPT และ LlamaParse API

## โครงสร้างโปรเจค

```
extract-ocr-map/
├── data/
│   ├── data-input/          # ไฟล์ต้นฉบับ (JPG, DOCX, etc.)
│   ├── data-parsed-md/      # ไฟล์ที่แปลงเป็น Markdown
│   ├── data-output-json/    # ไฟล์ JSON แยกตามเอกสาร
│   └── json-merge/          # ไฟล์ JSON รวมทั้งหมด
├── script/
│   ├── 00-llama-parsed-ocr.py    # แปลงเอกสารเป็น Markdown
│   ├── 01-convert-md_to_json.py  # แปลง Markdown เป็น JSON
│   └── 02-merge-json.py          # รวมไฟล์ JSON
├── main.py                  # สคริปต์หลักสำหรับรัน pipeline
├── requirements.txt         # รายการ packages ที่จำเป็น
└── .env                     # ไฟล์ตั้งค่า API keys
```

## การติดตั้ง

1. ติดตั้ง Python packages ที่จำเป็น:
```bash
# วิธีที่ 1: ติดตั้งจาก requirements.txt (แนะนำ)
pip install -r requirements.txt
```
# วิธีที่ 2: ติดตั้งทีละ package
```bash
pip install openai python-dotenv llama-parse llama-index
```

2. สร้างไฟล์ `.env` ในโฟลเดอร์หลักของโปรเจค และกำหนดค่า API keys:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Llama Cloud Configuration
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
```

> **หมายเหตุ**: คุณต้องมี API keys ที่ถูกต้องจาก OpenAI และ Llama Cloud เพื่อใช้งานโปรเจคนี้

## ขั้นตอนการใช้งาน

### 1. เตรียมไฟล์ต้นฉบับ
- นำไฟล์เอกสารที่ต้องการประมวลผล (JPG, DOCX, PPTX, etc.) ไปวางในโฟลเดอร์ `data/data-input/`
- สามารถจัดไฟล์เป็นโฟลเดอร์ย่อยได้

### 2. รัน Pipeline
มี 2 วิธีในการรัน pipeline:

#### วิธีที่ 1: รันแบบง่าย (ใช้ default paths)
```bash
python main.py
```
- จะใช้ default paths ทั้งหมด:
  - Input: `./data/data-input/`
  - Parsed MD: `./data/data-parsed-md/`
  - Output JSON: `./data/data-output-json/`
  - Merged JSON: `./data/json-merge/`

#### วิธีที่ 2: รันแบบกำหนด paths เอง
```bash
python main.py \
  --input-dir ./custom/input \
  --parsed-md-dir ./custom/parsed-md \
  --output-json-dir ./custom/json \
  --merged-json-dir ./custom/merged
```

### 3. ขั้นตอนการทำงานของ Pipeline
Pipeline จะทำงานตามลำดับดังนี้:

1. **ขั้นตอนที่ 1**: แปลงเอกสารเป็น Markdown
   - อ่านไฟล์จาก `data/data-input/`
   - แปลงเอกสารเป็น Markdown โดยใช้ LlamaParse และ OpenAI
   - บันทึกผลลัพธ์ใน `data/data-parsed-md/`

2. **ขั้นตอนที่ 2**: แปลง Markdown เป็น JSON
   - อ่านไฟล์ Markdown จาก `data/data-parsed-md/`
   - แปลงข้อมูลเป็น JSON โดยใช้ OpenAI GPT
   - บันทึกผลลัพธ์ใน `data/data-output-json/`

3. **ขั้นตอนที่ 3**: รวมไฟล์ JSON
   - รวมไฟล์ JSON ทั้งหมดจาก `data/data-output-json/`
   - สร้างไฟล์ JSON เดียวใน `data/json-merge/merged_land_deeds.json`

## โครงสร้างข้อมูล JSON

ไฟล์ JSON ที่ได้จะมีโครงสร้างดังนี้:
```json
{
  "total_records": <จำนวนรายการทั้งหมด>,
  "data": [
    {
      "เลขโฉนดที่ดิน": "<string>",
      "หน้าสำรวจ": "<string>",
      "เลขที่ดิน": "<string>",
      "ระวาง": "<string>",
      "ตำบล": "<string>",
      "อำเภอ": "<string>",
      "จังหวัด": "<string>",
      "เนื้อที่": "<string>",
      "ราคาประเมินที่ดิน": "<string>",
      "ค่าพิกัดแปลง": "<latitude,longitude>",
      "ข้อมูลการเดินทาง": "<string>",
      "source_file": "<path/to/original/file>"
    },
    // ... รายการอื่นๆ ...
  ]
}
```

## การแก้ไขปัญหา

1. **ปัญหา API Keys**:
   - ตรวจสอบว่ามีไฟล์ `.env` ในโฟลเดอร์หลักของโปรเจค
   - ตรวจสอบว่า API keys ถูกต้องและยังไม่หมดอายุ
   - ตรวจสอบว่า model ที่ใช้ (`OPENAI_MODEL`) ถูกต้อง

2. **ปัญหาไฟล์ไม่พบ**:
   - ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ `data/data-input/`
   - ตรวจสอบสิทธิ์การเข้าถึงไฟล์
   - ตรวจสอบว่า path ที่ระบุถูกต้อง

3. **ปัญหา API**:
   - ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
   - ตรวจสอบโควต้าการใช้งาน API
   - ตรวจสอบ log file สำหรับรายละเอียดข้อผิดพลาด

4. **ปัญหา JSON ไม่ถูกต้อง**:
   - ตรวจสอบรูปแบบของไฟล์ Markdown ต้นฉบับ
   - ตรวจสอบการตอบกลับจาก OpenAI API
   - ตรวจสอบ log file สำหรับรายละเอียดข้อผิดพลาด

## Log Files

- Pipeline จะสร้าง log file ในรูปแบบ `pipeline_YYYYMMDD_HHMMSS.log`
- Log file จะเก็บข้อมูลการทำงานทั้งหมด รวมถึงข้อผิดพลาดที่เกิดขึ้น
- ตรวจสอบ log file เพื่อดูรายละเอียดการทำงานและแก้ไขปัญหา

## หมายเหตุ

- ระบบจะข้ามไฟล์ที่ประมวลผลแล้วในแต่ละขั้นตอน
- ข้อมูลจะถูกเรียงตามเลขโฉนดที่ดิน
- หากมีข้อผิดพลาดในการประมวลผล จะมีการแสดงข้อความแจ้งเตือน
- ไฟล์ JSON รักษาการเข้ารหัส UTF-8 สำหรับภาษาไทย

## การแก้ไขปัญหา

1. หากไม่พบไฟล์ในโฟลเดอร์ input:
   - ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ `data/data-input/`
   - ตรวจสอบสิทธิ์การเข้าถึงไฟล์

2. หากเกิดข้อผิดพลาด API:
   - ตรวจสอบ API keys ในไฟล์ `.env`
   - ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
   - ตรวจสอบโควต้าการใช้งาน API

3. หากข้อมูล JSON ไม่ถูกต้อง:
   - ตรวจสอบรูปแบบของไฟล์ Markdown ต้นฉบับ
   - ตรวจสอบการตอบกลับจาก OpenAI API 