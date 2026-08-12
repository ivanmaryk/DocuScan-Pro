# 📄 DocuScan Pro — сканируй, выпрямляй, распознавай

> «Сфоткал, отсканировал, прочитал — всё в одной утилите»

**DocuScan Pro** — это набор консольных утилит для автоматического обнаружения границ документа на фотографии, коррекции перспективы (выпрямление) и распознавания текста с помощью OCR (Tesseract).  
Программа превращает сфотографированный документ в ровный скан и извлекает из него текст.

## 🚀 Особенности
- 🧠 Автоматическое обнаружение четырёх углов документа (алгоритм контуров + аппроксимация).
- 🔄 Коррекция перспективы (преобразование гомографии) — получается ровный прямоугольник.
- 📖 Распознавание текста с помощью Tesseract OCR (поддержка английского и других языков).
- 📸 Поддержка форматов: JPG, PNG, BMP, TIFF.
- 📁 Пакетная обработка (передайте папку, и всё будет обработано).
- 🎨 Цветной вывод в терминале, прогресс-бар.
- 💾 Сохранение результатов: отсканированное изображение + распознанный текст.

## 🛠️ Установка и запуск

Для каждого языка — минимальные зависимости (OpenCV + Tesseract).

| Язык       | Библиотека(и)                                  | Команда запуска                         |
|------------|------------------------------------------------|-----------------------------------------|
| Python     | `opencv-python`, `pytesseract`, `Pillow`       | `python doc_scanner.py image.jpg`       |
| Go         | `gocv`, `gosseract`                            | `go run doc_scanner.go image.jpg`       |
| JavaScript | `opencv4nodejs`, `tesseract.js`                | `node doc_scanner.js image.jpg`         |
| Java       | `OpenCV (JavaCV)`, `Tess4J`                    | `javac -cp .:opencv.jar:tess4j.jar ...` |
| C#         | `OpenCVSharp`, `Tesseract.NET`                 | `dotnet run image.jpg`                  |
| Rust       | `opencv-rs` или `image-rs`, `rusty-tesseract`  | `cargo run -- image.jpg`                |
| Ruby       | `rmagick` + `rtesseract`                       | `ruby doc_scanner.rb image.jpg`         |
| PHP        | `Imagick` + `thiagoalessio/tesseract_ocr`      | `php doc_scanner.php image.jpg`         |

> Для работы всех скриптов требуется предварительно установленный Tesseract OCR на системе.
> На Ubuntu/Debian: `sudo apt install tesseract-ocr`
> На macOS: `brew install tesseract`
> На Windows: скачайте установщик с [GitHub](https://github.com/tesseract-ocr/tesseract/releases)

## 📖 Пример использования

```bash
$ python doc_scanner.py photo.jpg
Вывод:

text
📄 DocuScan Pro (Python)
📂 Обработка: photo.jpg
🔍 Ищем контуры документа... ✅
📐 Коррекция перспективы... ✅
📖 Распознавание текста... ✅

Результат:
─────────────────────────────────────────
Invoice #12345
Date: 2025-01-15
Total: $99.99
─────────────────────────────────────────

💾 Сохранено: photo_scanned.jpg
💾 Сохранено: photo_scanned.txt
🤝 Вклад
Принимаются улучшения, новые языки, фичи.

📜 Лицензия
MIT — используйте свободно.

Автор: Ваш покорный слуга
