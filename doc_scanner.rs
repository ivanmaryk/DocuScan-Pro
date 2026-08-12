// doc_scanner.rs — Rust версия

use std::env;
use std::fs;
use std::path::Path;
use std::time::Instant;
use image::open;
use opencv::{core, imgcodecs, imgproc, prelude::*, types};
use rusty_tesseract::{Args, Image};

fn scan_document(input_path: &str) -> Result<opencv::core::Mat, Box<dyn std::error::Error>> {
    let img = imgcodecs::imread(input_path, imgcodecs::IMREAD_COLOR)?;
    if img.empty() {
        return Err("Не удалось загрузить изображение".into());
    }
    let orig = img.clone();
    let ratio = img.rows() as f64 / 500.0;
    let mut resized = core::Mat::default();
    imgproc::resize(&img, &mut resized, core::Size {
        width: (img.cols() as f64 / ratio) as i32,
        height: 500,
    }, 0.0, 0.0, imgproc::INTER_LINEAR)?;

    let mut gray = core::Mat::default();
    imgproc::cvt_color(&resized, &mut gray, imgproc::COLOR_BGR2GRAY, 0)?;
    let mut blurred = core::Mat::default();
    imgproc::gaussian_blur(&gray, &mut blurred, core::Size { width: 5, height: 5 }, 0.0, 0.0, core::BORDER_DEFAULT)?;
    let mut edged = core::Mat::default();
    imgproc::canny(&blurred, &mut edged, 75.0, 200.0, 3, false)?;

    let mut contours = types::VectorOfVectorOfPoint::new();
    let mut hierarchy = core::Mat::default();
    imgproc::find_contours(&edged, &mut contours, &mut hierarchy, imgproc::RETR_LIST, imgproc::CHAIN_APPROX_SIMPLE, core::Point::default())?;

    let mut screen_cnt = None;
    let contours_len = contours.len();
    for i in 0..contours_len {
        let cnt = contours.get(i)?;
        let peri = imgproc::arc_length(&cnt, true)?;
        let mut approx = types::VectorOfPoint2f::new();
        imgproc::approx_poly_dp(&types::VectorOfPoint2f::from(cnt), &mut approx, 0.02 * peri, true)?;
        if approx.len() == 4 {
            let mut points = types::VectorOfPoint::new();
            for p in approx {
                points.push(core::Point { x: p.x as i32, y: p.y as i32 });
            }
            screen_cnt = Some(points);
            break;
        }
    }
    if screen_cnt.is_none() {
        return Err("Не найден четырёхугольный контур".into());
    }
    Ok(orig)
}

fn ocr_image(img: &opencv::core::Mat, lang: &str) -> Result<String, Box<dyn std::error::Error>> {
    let tmp_file = "temp_ocr.jpg";
    imgcodecs::imwrite(tmp_file, img, &core::Vector::default())?;
    let image = Image::from_path(tmp_file)?;
    let args = Args::default().lang(lang);
    let text = rusty_tesseract::image_to_string(&image, &args)?;
    fs::remove_file(tmp_file)?;
    Ok(text.trim().to_string())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    let mut image_path = None;
    let mut lang = "eng".to_string();

    let mut i = 1;
    while i < args.len() {
        if args[i] == "-l" || args[i] == "--lang" {
            lang = args[i+1].clone();
            i += 2;
        } else if !args[i].starts_with("-") {
            image_path = Some(args[i].clone());
            i += 1;
        } else {
            i += 1;
        }
    }

    let image_path = image_path.ok_or("Usage: cargo run -- <image> [-l lang]")?;

    if !Path::new(&image_path).exists() {
        eprintln!("\x1b[31m❌ Файл не найден: {}\x1b[0m", image_path);
        std::process::exit(1);
    }

    println!("\x1b[36m📄 DocuScan Pro (Rust)\x1b[0m");
    println!("📂 Обработка: {}", image_path);

    let start = Instant::now();

    let warped = scan_document(&image_path)?;
    let text = ocr_image(&warped, &lang)?;
    let elapsed = start.elapsed().as_secs_f64();

    let out_img = image_path.replace(Path::new(&image_path).extension().unwrap().to_str().unwrap(), "scanned.jpg");
    let out_txt = image_path.replace(Path::new(&image_path).extension().unwrap().to_str().unwrap(), "scanned.txt");

    imgcodecs::imwrite(&out_img, &warped, &core::Vector::default())?;
    fs::write(&out_txt, &text)?;

    println!("\n\x1b[32mРезультат:\x1b[0m");
    println!("{}", "─".repeat(50));
    println!("{}", if text.is_empty() { "[Текст не распознан]" } else { &text });
    println!("{}", "─".repeat(50));

    println!("\x1b[36m📊 Статистика:\x1b[0m");
    println!("  Время: {:.2} сек", elapsed);
    println!("  Слов: {}", text.split_whitespace().count());
    println!("  Символов: {}", text.len());
    println!("\x1b[32m💾 Сохранено: {}\x1b[0m", out_img);
    println!("\x1b[32m💾 Сохранено: {}\x1b[0m", out_txt);

    Ok(())
}
