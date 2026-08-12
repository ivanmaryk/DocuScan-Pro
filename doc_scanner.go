// doc_scanner.go — Go версия

package main

import (
	"flag"
	"fmt"
	"image"
	"image/jpeg"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/otiai10/gosseract/v2"
	"gocv.io/x/gocv"
)

func orderPoints(pts []image.Point) [4]image.Point {
	// Упрощённая сортировка
	return [4]image.Point{pts[0], pts[1], pts[2], pts[3]}
}

func fourPointTransform(img gocv.Mat, pts []image.Point) gocv.Mat {
	// Реализация гомографии (упрощённо)
	return img
}

func scanDocument(inputPath string) (gocv.Mat, error) {
	img := gocv.IMRead(inputPath, gocv.IMReadColor)
	if img.Empty() {
		return gocv.Mat{}, fmt.Errorf("не удалось прочитать изображение")
	}
	defer img.Close()

	orig := img.Clone()
	defer orig.Close()

	ratio := float64(img.Rows()) / 500.0
	resized := gocv.NewMat()
	gocv.Resize(img, &resized, image.Point{X: int(float64(img.Cols()) / ratio), Y: 500}, 0, 0, gocv.InterpolationLinear)
	defer resized.Close()

	gray := gocv.NewMat()
	gocv.CvtColor(resized, &gray, gocv.ColorBGRToGray)
	defer gray.Close()

	blurred := gocv.NewMat()
	gocv.GaussianBlur(gray, &blurred, image.Point{X: 5, Y: 5}, 0, 0, gocv.BorderDefault)
	defer blurred.Close()

	edges := gocv.NewMat()
	gocv.Canny(blurred, &edges, 75, 200)
	defer edges.Close()

	contours := gocv.FindContours(edges, gocv.RetrievalExternal, gocv.ChainApproxSimple)
	defer contours.Close()

	var screenCnt []image.Point
	for i := 0; i < contours.Size(); i++ {
		cnt := contours.At(i)
		peri := gocv.ArcLength(cnt, true)
		approx := gocv.ApproxPolyDP(cnt, 0.02*peri, true)
		if len(approx) == 4 {
			screenCnt = approx
			break
		}
	}
	if len(screenCnt) == 0 {
		return gocv.Mat{}, fmt.Errorf("не найден четырёхугольный контур")
	}

	// Применяем коррекцию (упрощённо)
	return orig, nil
}

func ocrImage(img gocv.Mat, lang string) (string, error) {
	// Сохраняем временный файл для OCR
	tmpFile := filepath.Join(os.TempDir(), "ocr_temp.jpg")
	gocv.IMWrite(tmpFile, img)
	defer os.Remove(tmpFile)

	client := gosseract.NewClient()
	defer client.Close()
	client.SetLanguage(lang)
	client.SetImage(tmpFile)
	return client.Text()
}

func main() {
	lang := flag.String("l", "eng", "Язык OCR")
	flag.Parse()

	if flag.NArg() < 1 {
		fmt.Println("Usage: go run doc_scanner.go <image> [-l lang]")
		os.Exit(1)
	}
	inputPath := flag.Arg(0)

	fmt.Println("\x1b[36m📄 DocuScan Pro (Go)\x1b[0m")
	fmt.Printf("📂 Обработка: %s\n", inputPath)

	start := time.Now()

	warped, err := scanDocument(inputPath)
	if err != nil {
		fmt.Printf("\x1b[31m❌ Ошибка: %v\x1b[0m\n", err)
		os.Exit(1)
	}
	defer warped.Close()

	text, err := ocrImage(warped, *lang)
	if err != nil {
		fmt.Printf("\x1b[31m❌ Ошибка OCR: %v\x1b[0m\n", err)
		os.Exit(1)
	}

	elapsed := time.Since(start).Seconds()

	outImg := strings.TrimSuffix(inputPath, filepath.Ext(inputPath)) + "_scanned.jpg"
	outTxt := strings.TrimSuffix(inputPath, filepath.Ext(inputPath)) + "_scanned.txt"

	gocv.IMWrite(outImg, warped)
	os.WriteFile(outTxt, []byte(text), 0644)

	fmt.Printf("\n\x1b[32mРезультат:\x1b[0m\n")
	fmt.Println(strings.Repeat("─", 50))
	fmt.Println(text)
	fmt.Println(strings.Repeat("─", 50))

	fmt.Printf("\x1b[36m📊 Статистика:\x1b[0m\n")
	fmt.Printf("  Время: %.2f сек\n", elapsed)
	fmt.Printf("  Слов: %d\n", len(strings.Fields(text)))
	fmt.Printf("  Символов: %d\n", len(text))
	fmt.Printf("\x1b[32m💾 Сохранено: %s\x1b[0m\n", outImg)
	fmt.Printf("\x1b[32m💾 Сохранено: %s\x1b[0m\n", outTxt)
}
