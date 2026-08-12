

### 1. `doc_scanner.py` (Python)

```python
# doc_scanner.py — Python версия

import cv2
import numpy as np
import pytesseract
import sys
import os
import time
from PIL import Image
from colorama import init, Fore, Style

init(autoreset=True)

def order_points(pts):
    """Сортировка точек: верх-левый, верх-правый, ниж-правый, ниж-левый"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """Применяет перспективное преобразование"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def scan_document(image_path, lang='eng'):
    """Основная функция сканирования и OCR"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")

    orig = image.copy()
    ratio = image.shape[0] / 500.0
    image_resized = cv2.resize(image, (int(image.shape[1] / ratio), 500))
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        raise ValueError("Не удалось найти четырёхугольный контур")

    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    return warped

def ocr_image(image, lang='eng'):
    """Распознаёт текст с изображения"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil_img = Image.fromarray(thresh)
    text = pytesseract.image_to_string(pil_img, lang=lang)
    return text.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python doc_scanner.py <image_path> [-l lang]")
        sys.exit(1)

    image_path = sys.argv[1]
    lang = 'eng'
    if '-l' in sys.argv:
        idx = sys.argv.index('-l')
        if idx + 1 < len(sys.argv):
            lang = sys.argv[idx + 1]

    if not os.path.exists(image_path):
        print(f"{Fore.RED}❌ Файл не найден: {image_path}")
        sys.exit(1)

    print(f"{Fore.CYAN}📄 DocuScan Pro (Python)")
    print(f"📂 Обработка: {image_path}")

    start = time.time()

    try:
        print("🔍 Ищем контуры документа...", end=' ')
        warped = scan_document(image_path)
        print(f"{Fore.GREEN}✅")

        print("📖 Распознавание текста...", end=' ')
        text = ocr_image(warped, lang)
        print(f"{Fore.GREEN}✅")

        elapsed = time.time() - start

        out_img = os.path.splitext(image_path)[0] + "_scanned.jpg"
        out_txt = os.path.splitext(image_path)[0] + "_scanned.txt"

        cv2.imwrite(out_img, warped)
        with open(out_txt, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"\n{Fore.GREEN}Результат:{Style.RESET_ALL}")
        print("─" * 50)
        print(text if text else "[Текст не распознан]")
        print("─" * 50)

        print(f"{Fore.CYAN}📊 Статистика:{Style.RESET_ALL}")
        print(f"  Время: {elapsed:.2f} сек")
        print(f"  Слов: {len(text.split())}")
        print(f"  Символов: {len(text)}")
        print(f"{Fore.GREEN}💾 Сохранено: {out_img}")
        print(f"{Fore.GREEN}💾 Сохранено: {out_txt}")

    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
