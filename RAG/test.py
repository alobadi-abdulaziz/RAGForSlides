import easyocr
import os
import fitz  # PyMuPDF

def process_document(file_path):
    """
    هذه الدالة تأخذ مسار ملف (صورة أو PDF)، وتقوم بتشغيل EasyOCR عليه،
    ثم تطبع النصوص التي تم اكتشافها لكل صفحة والنص الكامل في النهاية.
    """
    # 1. التحقق من وجود الملف
    if not os.path.exists(file_path):
        print(f"خطأ: لم يتم العثور على الملف في المسار '{file_path}'")
        print("يرجى إنشاء ملف PDF أو صورة وحفظه بهذا الاسم.")
        return

    # 2. إنشاء قارئ OCR.
    print("...جاري تحميل نماذج EasyOCR (قد يستغرق هذا بعض الوقت في المرة الأولى)")
    reader = easyocr.Reader(['ar', 'en'], gpu=False) 
    print("تم تحميل النماذج بنجاح.")

    # 3. التحقق من نوع الملف والبدء بالمعالجة
    print(f"\n...جاري معالجة الملف '{file_path}'")
    
    # سيتم تجميع كل النصوص هنا
    all_texts = []

    if file_path.lower().endswith('.pdf'):
        # معالجة ملف PDF
        try:
            doc = fitz.open(file_path)
            print(f"تم العثور على {len(doc)} صفحة في ملف الـ PDF.")
            for i, page in enumerate(doc):
                print(f"\n--- جاري قراءة الصفحة رقم {i+1} ---")
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                results = reader.readtext(img_bytes)
                
                if not results:
                    print("  لم يتم اكتشاف أي نص في هذه الصفحة.")
                    continue

                # تجميع نصوص الصفحة الحالية
                page_text_parts = []
                for (bbox, text, prob) in results:
                    print(f'  النص: "{text}"، درجة الثقة: {prob:.2f}')
                    page_text_parts.append(text)
                
                # إضافة نصوص الصفحة كاملة إلى القائمة الرئيسية
                all_texts.append(" ".join(page_text_parts))

            doc.close()
        except Exception as e:
            print(f"حدث خطأ أثناء معالجة ملف الـ PDF: {e}")
            return
            
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        # معالجة ملف الصورة
        results = reader.readtext(file_path)
        if results:
            for (bbox, text, prob) in results:
                print(f'  النص: "{text}"، درجة الثقة: {prob:.2f}')
                all_texts.append(text)
    else:
        print("خطأ: صيغة الملف غير مدعومة. يرجى استخدام PDF أو ملف صورة (PNG, JPG).")
        return

    # 4. طباعة النص الكامل الذي تم تجميعه من كل الصفحات
    print("\n\n--- النص الكامل الذي تم استخراجه من المستند ---")
    full_document_text = "\n\n--- صفحة جديدة ---\n\n".join(all_texts)
    print(full_document_text)
    print("\n--- نهاية التقرير ---\n")

if __name__ == '__main__':
    # --- هام ---
    # 1. لتشغيل هذا الكود، تحتاج لتثبيت مكتبة PyMuPDF:
    # pip install PyMuPDF

    # 2. حدد مسار الملف التجريبي (يمكن أن يكون صورة أو PDF)
    document_file = '01-Introduction (1).pptx'
    
    # 3. تأكد من إنشاء هذا الملف في نفس المجلد الذي يوجد فيه هذا السكربت
    process_document(document_file)

