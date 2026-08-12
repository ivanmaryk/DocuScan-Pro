// doc_scanner.java — Java версия

import net.sourceforge.tess4j.*;
import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class doc_scanner {
    static { System.loadLibrary(Core.NATIVE_LIBRARY_NAME); }

    public static Mat scanDocument(String inputPath) throws Exception {
        Mat src = Imgcodecs.imread(inputPath);
        if (src.empty()) {
            throw new Exception("Не удалось загрузить изображение");
        }
        Mat orig = src.clone();
        double ratio = src.rows() / 500.0;
        Mat resized = new Mat();
        Imgproc.resize(src, resized, new Size(src.cols() / ratio, 500));

        Mat gray = new Mat();
        Imgproc.cvtColor(resized, gray, Imgproc.COLOR_BGR2GRAY);
        Mat blurred = new Mat();
        Imgproc.GaussianBlur(gray, blurred, new Size(5,5), 0);
        Mat edged = new Mat();
        Imgproc.Canny(blurred, edged, 75, 200);

        List<MatOfPoint> contours = new ArrayList<>();
        Mat hierarchy = new Mat();
        Imgproc.findContours(edged, contours, hierarchy, Imgproc.RETR_LIST, Imgproc.CHAIN_APPROX_SIMPLE);

        contours.sort((a, b) -> Double.compare(Imgproc.contourArea(b), Imgproc.contourArea(a)));
        contours = contours.subList(0, Math.min(5, contours.size()));

        MatOfPoint2f screenCnt = null;
        for (MatOfPoint cnt : contours) {
            MatOfPoint2f cnt2f = new MatOfPoint2f(cnt.toArray());
            double peri = Imgproc.arcLength(cnt2f, true);
            MatOfPoint2f approx = new MatOfPoint2f();
            Imgproc.approxPolyDP(cnt2f, approx, 0.02 * peri, true);
            if (approx.toArray().length == 4) {
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

    public static String ocrImage(Mat image, String lang) throws Exception {
        String tmpFile = "temp_ocr.jpg";
        Imgcodecs.imwrite(tmpFile, image);
        Tesseract tesseract = new Tesseract();
        tesseract.setLanguage(lang);
        String text = tesseract.doOCR(new File(tmpFile));
        new File(tmpFile).delete();
        return text.trim();
    }

    public static void main(String[] args) throws Exception {
        String imagePath = null;
        String lang = "eng";

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("-l") || args[i].equals("--lang")) {
                lang = args[++i];
            } else if (!args[i].startsWith("-")) {
                imagePath = args[i];
            }
        }

        if (imagePath == null) {
            System.out.println("Usage: java doc_scanner <image> [-l lang]");
            System.exit(1);
        }

        if (!Files.exists(Paths.get(imagePath))) {
            System.out.println("\u001B[31m❌ Файл не найден: " + imagePath + "\u001B[0m");
            System.exit(1);
        }

        System.out.println("\u001B[36m📄 DocuScan Pro (Java)\u001B[0m");
        System.out.println("📂 Обработка: " + imagePath);

        long start = System.currentTimeMillis();

        try {
            Mat warped = scanDocument(imagePath);
            String text = ocrImage(warped, lang);
            double elapsed = (System.currentTimeMillis() - start) / 1000.0;

            String outImg = imagePath.replaceFirst("\\.[^.]+$", "") + "_scanned.jpg";
            String outTxt = imagePath.replaceFirst("\\.[^.]+$", "") + "_scanned.txt";

            Imgcodecs.imwrite(outImg, warped);
            Files.write(Paths.get(outTxt), text.getBytes());

            System.out.println("\n\u001B[32mРезультат:\u001B[0m");
            System.out.println("─".repeat(50));
            System.out.println(text.isEmpty() ? "[Текст не распознан]" : text);
            System.out.println("─".repeat(50));

            System.out.println("\u001B[36m📊 Статистика:\u001B[0m");
            System.out.printf("  Время: %.2f сек\n", elapsed);
            System.out.printf("  Слов: %d\n", text.isEmpty() ? 0 : text.split("\\s+").length);
            System.out.printf("  Символов: %d\n", text.length());
            System.out.println("\u001B[32m💾 Сохранено: " + outImg + "\u001B[0m");
            System.out.println("\u001B[32m💾 Сохранено: " + outTxt + "\u001B[0m");
        } catch (Exception e) {
            System.out.println("\u001B[31m❌ Ошибка: " + e.getMessage() + "\u001B[0m");
            System.exit(1);
        }
    }
}
