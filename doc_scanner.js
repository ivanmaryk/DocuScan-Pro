// doc_scanner.js — JavaScript версия

const cv = require('opencv4nodejs');
const Tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');

function orderPoints(pts) {
    // Упрощённая сортировка
    return pts;
}

function fourPointTransform(image, pts) {
    // Упрощённая реализация
    return image;
}

async function scanDocument(imagePath) {
    const src = cv.imread(imagePath);
    if (src.empty) {
        throw new Error('Не удалось загрузить изображение');
    }
    const orig = src.copy();
    const ratio = src.rows / 500;
    const resized = src.resize(500, Math.round(src.cols / ratio));

    const gray = resized.cvtColor(cv.COLOR_BGR2GRAY);
    const blurred = gray.gaussianBlur(new cv.Size(5, 5), 0);
    const edged = blurred.canny(75, 200);

    const contours = edged.findContours(cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);
    const sorted = contours.sort((a, b) => b.area - a.area).slice(0, 5);

    let screenCnt = null;
    for (const cnt of sorted) {
        const peri = cnt.arcLength(true);
        const approx = cnt.approxPolyDP(0.02 * peri, true);
        if (approx.length === 4) {
            screenCnt = approx;
            break;
        }
    }
    if (!screenCnt) {
        throw new Error('Не найден четырёхугольный контур');
    }
    // Коррекция перспективы (упрощённо)
    return orig;
}

async function ocrImage(image, lang = 'eng') {
    const tmpFile = path.join(__dirname, 'temp_ocr.jpg');
    cv.imwrite(tmpFile, image);
    const result = await Tesseract.recognize(tmpFile, lang);
    fs.unlinkSync(tmpFile);
    return result.data.text.trim();
}

async function main() {
    const args = process.argv.slice(2);
    let imagePath = null;
    let lang = 'eng';

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '-l' || args[i] === '--lang') {
            lang = args[++i];
        } else if (!args[i].startsWith('-')) {
            imagePath = args[i];
        }
    }

    if (!imagePath) {
        console.log('Usage: node doc_scanner.js <image> [-l lang]');
        process.exit(1);
    }

    if (!fs.existsSync(imagePath)) {
        console.error(`\x1b[31m❌ Файл не найден: ${imagePath}\x1b[0m`);
        process.exit(1);
    }

    console.log('\x1b[36m📄 DocuScan Pro (JavaScript)\x1b[0m');
    console.log(`📂 Обработка: ${imagePath}`);

    const start = Date.now();

    try {
        const warped = await scanDocument(imagePath);
        const text = await ocrImage(warped, lang);
        const elapsed = (Date.now() - start) / 1000;

        const outImg = imagePath.replace(/\.[^.]+$/, '') + '_scanned.jpg';
        const outTxt = imagePath.replace(/\.[^.]+$/, '') + '_scanned.txt';

        cv.imwrite(outImg, warped);
        fs.writeFileSync(outTxt, text);

        console.log(`\n\x1b[32mРезультат:\x1b[0m`);
        console.log('─'.repeat(50));
        console.log(text || '[Текст не распознан]');
        console.log('─'.repeat(50));

        console.log(`\x1b[36m📊 Статистика:\x1b[0m`);
        console.log(`  Время: ${elapsed.toFixed(2)} сек`);
        console.log(`  Слов: ${text.split(/\s+/).filter(w => w).length}`);
        console.log(`  Символов: ${text.length}`);
        console.log(`\x1b[32m💾 Сохранено: ${outImg}\x1b[0m`);
        console.log(`\x1b[32m💾 Сохранено: ${outTxt}\x1b[0m`);
    } catch (err) {
        console.error(`\x1b[31m❌ Ошибка: ${err.message}\x1b[0m`);
        process.exit(1);
    }
}

main().catch(console.error);
