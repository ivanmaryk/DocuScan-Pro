// doc_scanner.cs — C# версия

using System;
using System.IO;
using System.Linq;
using OpenCvSharp;
using Tesseract;

class DocScanner {
    static Mat ScanDocument(string inputPath) {
        var src = Cv2.ImRead(inputPath);
        if (src.Empty()) {
            throw new Exception("Не удалось загрузить изображение");
        }
        var orig = src.Clone();
        double ratio = src.Rows / 500.0;
        var resized = new Mat();
        Cv2.Resize(src, resized, new Size(src.Cols / ratio, 500));

        var gray = new Mat();
        Cv2.CvtColor(resized, gray, ColorConversionCodes.BGR2GRAY);
        var blurred = new Mat();
        Cv2.GaussianBlur(gray, blurred, new Size(5, 5), 0);
        var edged = new Mat();
        Cv2.Canny(blurred, edged, 75, 200);

        var contours = Cv2.FindContours(edged, RetrievalModes.List, ContourApproximationModes.ApproxSimple);
        var sorted = contours.OrderByDescending(c => Cv2.ContourArea(c)).Take(5).ToList();

        Point[][] screenCnt = null;
        foreach (var cnt in sorted) {
            var peri = Cv2.ArcLength(cnt, true);
            var approx = Cv2.ApproxPolyDP(cnt, 0.02 * peri, true);
            if (approx.Length == 4) {
                screenCnt = approx;
                break;
            }
        }
        if (screenCnt == null) {
            throw new Exception("Не найден четырёхугольный контур");
        }
        // Упрощённая коррекция
        return orig;
    }

    static string OcrImage(Mat image, string lang) {
        string tmpFile = Path.GetTempFileName() + ".jpg";
        Cv2.ImWrite(tmpFile, image);
        using (var engine = new TesseractEngine("./tessdata", lang, EngineMode.Default)) {
            using (var img = Pix.LoadFromFile(tmpFile)) {
                using (var page = engine.Process(img)) {
                    File.Delete(tmpFile);
                    return page.GetText().Trim();
                }
            }
        }
    }

    static void Main(string[] args) {
        string imagePath = null;
        string lang = "eng";

        for (int i = 0; i < args.Length; i++) {
            if (args[i] == "-l" || args[i] == "--lang") {
                lang = args[++i];
            } else if (!args[i].StartsWith("-")) {
                imagePath = args[i];
            }
        }

        if (imagePath == null) {
            Console.WriteLine("Usage: dotnet run <image> [-l lang]");
            return;
        }

        if (!File.Exists(imagePath)) {
            Console.WriteLine($"\u001B[31m❌ Файл не найден: {imagePath}\u001B[0m");
            return;
        }

        Console.WriteLine("\u001B[36m📄 DocuScan Pro (C#)\u001B[0m");
        Console.WriteLine($"📂 Обработка: {imagePath}");

        var start = DateTime.Now;

        try {
            var warped = ScanDocument(imagePath);
            var text = OcrImage(warped, lang);
            var elapsed = (DateTime.Now - start).TotalSeconds;

            var outImg = Path.GetFileNameWithoutExtension(imagePath) + "_scanned.jpg";
            var outTxt = Path.GetFileNameWithoutExtension(imagePath) + "_scanned.txt";

            Cv2.ImWrite(outImg, warped);
            File.WriteAllText(outTxt, text);

            Console.WriteLine($"\n\u001B[32mРезультат:\u001B[0m");
            Console.WriteLine(new string('─', 50));
            Console.WriteLine(string.IsNullOrEmpty(text) ? "[Текст не распознан]" : text);
            Console.WriteLine(new string('─', 50));

            Console.WriteLine($"\u001B[36m📊 Статистика:\u001B[0m");
            Console.WriteLine($"  Время: {elapsed:F2} сек");
            Console.WriteLine($"  Слов: {text.Split(new[] {' ', '\n'}, StringSplitOptions.RemoveEmptyEntries).Length}");
            Console.WriteLine($"  Символов: {text.Length}");
            Console.WriteLine($"\u001B[32m💾 Сохранено: {outImg}\u001B[0m");
            Console.WriteLine($"\u001B[32m💾 Сохранено: {outTxt}\u001B[0m");
        } catch (Exception e) {
            Console.WriteLine($"\u001B[31m❌ Ошибка: {e.Message}\u001B[0m");
        }
    }
}
