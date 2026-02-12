# AI Information Extraction from Audio (Assignment)

โปรเจกต์นี้เป็นการพัฒนาระบบสกัดข้อมูลโครงสร้าง (Structured Data Extraction) จากไฟล์เสียง โดยใช้การประมวลผลแบบ Pipeline เพื่อเปลี่ยนข้อมูลไร้โครงสร้าง (Unstructured Data) ให้เป็นข้อมูลที่นำไปใช้งานต่อได้โดยอัตโนมัติ

---

## 1. System Architecture
สถาปัตยกรรมของระบบประกอบด้วย 3 ส่วนหลัก (Modular Workflow):

1.  **Speech-to-Text (STT) Stage**: ทำหน้าที่รับไฟล์เสียงและประมวลผลในระดับ Local เพื่อแปลงคำพูดเป็นข้อความดิบ (Raw Transcript)
2.  **Information Extraction (IE) Stage**: นำข้อความดิบส่งต่อให้ Large Language Model (Gemini 1.5/2.5 Flash) ทำหน้าที่เป็น Semantic Parser ในการวิเคราะห์และสรุปข้อมูลตามฟิลด์ที่กำหนด (Name, Surname, Gender, Phone, License Plate) ในรูปแบบ JSON
3.  **Validation & Logic Stage**: นำ JSON สรุปเข้าสู่กระบวนการตรวจสอบความถูกต้องด้วย Pydantic (Rule-based Validation) เพื่อประเมินสถานะของข้อมูลว่าเป็น COMPLETE หรือ INCOMPLETE

---

## 2. การเลือกใช้ STT (Faster-Whisper)
ระบบเลือกใช้โมเดล **Faster-Whisper (Medium)** โดยมีการปรับแต่ง (Optimization) ดังนี้:
-   **Model Size Selection**: เลือกใช้ขนาด Medium เนื่องจากมีความแม่นยำ (Accuracy) ในภาษาไทยสูงกว่าขนาด Small และผ่านการทดสอบว่าสามารถแก้ปัญหาการ Hallucination ของคำศัพท์เฉพาะได้ดี
-   **Compute Optimization**: กำหนด `compute_type="int8"` เพื่อลดภาระการประมวลผลและหน่วยความจำ VRAM ให้เหมาะสมกับฮาร์ดแวร์ระดับ GTX 1650 Ti (4GB)
-   **Device Configuration**: ใช้การตั้งค่า `device="auto"` เพื่อให้ระบบสามารถสลับระหว่างการประมวลผลบน CUDA (GPU) และ CPU ได้ตามความเหมาะสมของสภาพแวดล้อมโดยอัตโนมัติ

---

## 3. วิธีจัดการภาษาไทยและภาษาอังกฤษ (Multilingual Processing)
ระบบรองรับความเป็นธรรมชาติของคำพูด (Natural Language) ที่มีความซับซ้อน:
-   **Phonetic Correction**: มีการระบุใน System Instruction ให้ AI เข้าใจรูปแบบคำอ่านที่มักถูกแปลงผิดจากการฟัง (เช่น "ก็ขอ", "กอขอ") และทำการ Map กลับไปยังรหัสป้ายทะเบียนที่ถูกต้อง ("กข")
-   **Contextual Understanding**: AI สามารถแยกแยะความแตกต่างระหว่างชื่อบุคคลและเพศได้ แม้ว่า STT จะฟังคำบอกเพศเพี้ยนไป (เช่น "เพชรชาย" ตีความเป็นเพศ Male)
-   **Data Normalization**: มีกระบวนการทำความสะอาดข้อมูล (Cleanse) เบื้องหลัง เช่น การทำเบอร์โทรศัพท์ให้เป็นรูปแบบตัวเลขล้วน (Digit-only) ผ่านกระบวนการ Pydantic Validation

---

## 4. วิธีจัดการ Uncertainty (Data Validation & Ask-back)
ระบบมีกลไกในการจัดการกับความไม่แน่นอนของข้อมูล (Uncertainty Handling) ดังนี้:

1.  **Rule-based Validation**: ใช้ Pydantic ในการตรวจสอบโครงสร้างและกฎที่กำหนด (เช่น เบอร์โทรต้องมี 10 หลักและขึ้นต้นด้วย 0 หรือรูปแบบป้ายทะเบียนที่ถูกต้อง)
2.  **Incomplete Data Identification**: กรณีที่ข้อมูลขาดหายหรือตรวจสอบไม่ผ่านกฎ ระบบจะคืนผลลัพธ์เป็น Null และแจ้งสถานะ INCOMPLETE พร้อมระบุฟิลด์ที่ต้องการข้อมูลเพิ่มเติม
3.  **Ask-back Mechanism**: เมื่อสถานะเป็น INCOMPLETE ระบบจะส่งข้อมูลส่วนที่ขาดหายกลับไปยัง LLM เพื่อ Generate ประโยคคำถามที่สุภาพและชัดเจน (Context-aware asking) เพื่อขอข้อมูลจากผู้ใช้ซ้ำได้อย่างตรงจุด
