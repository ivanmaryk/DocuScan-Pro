<?php
// doc_scanner.php — PHP версия

require_once 'vendor/autoload.php';

use thiagoalessio\TesseractOCR\TesseractOCR;

$imagePath = null;
$lang = 'eng';

$args = array_slice($argv, 1);
for ($i = 0; $i < count($args); $i++) {
    if ($args[$i] == '-l' || $args[$i] == '--lang') {
        $lang = $args[++$i];
    } elseif (!str_starts_with($args[$i], '-')) {
        $imagePath = $args[$i];
    }
}

if (!$imagePath) {
    echo "Usage: php doc_scanner.php <image> [-l lang]\n";
    exit(1);
}

if (!file_exists($imagePath)) {
    echo "\033[31m❌ Файл не найден: $imagePath\033[0m\n";
    exit(1);
}

echo "\033[36m📄 DocuScan Pro (PHP)\033[0m\n";
echo "📂 Обработка: $imagePath\n";

$start = microtime(true);

try {
    // Загрузка и обработка изображения с помощью Imagick
    $img = new Imagick($imagePath);
    $ratio = $img->getImageHeight() / 500;
    $img->resizeImage($img->getImageWidth() / $ratio, 500, Imagick::FILTER_LANCZOS, 1);
    
    // Преобразование в градации серого и бинаризация (упрощённо)
    $img->transformImageColorspace(Imagick::COLORSPACE_GRAY);
    $img->thresholdImage(0.5 * Imagick::getQuantum());
    
    // Сохранение
    $outImg = pathinfo($imagePath, PATHINFO_FILENAME) . '_scanned.jpg';
    $img->writeImage($outImg);
    $img->clear();

    // OCR
    $ocr = new TesseractOCR($outImg);
    $ocr->lang($lang);
    $text = trim((string) $ocr);
    $elapsed = microtime(true) - $start;

    $outTxt = pathinfo($imagePath, PATHINFO_FILENAME) . '_scanned.txt';
    file_put_contents($outTxt, $text);

    echo "\n\033[32mРезультат:\033[0m\n";
    echo str_repeat("─", 50) . "\n";
    echo $text ?: "[Текст не распознан]\n";
    echo str_repeat("─", 50) . "\n";

    $words = count(array_filter(explode(' ', $text)));
    echo "\033[36m📊 Статистика:\033[0m\n";
    echo "  Время: " . number_format($elapsed, 2) . " сек\n";
    echo "  Слов: $words\n";
    echo "  Символов: " . strlen($text) . "\n";
    echo "\033[32m💾 Сохранено: $outImg\033[0m\n";
    echo "\033[32m💾 Сохранено: $outTxt\033[0m\n";
} catch (Exception $e) {
    echo "\033[31m❌ Ошибка: " . $e->getMessage() . "\033[0m\n";
    exit(1);
}
?>
