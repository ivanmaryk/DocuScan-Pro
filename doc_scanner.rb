# doc_scanner.rb — Ruby версия

require 'rtesseract'
require 'rmagick'
require 'optparse'
require 'time'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: ruby doc_scanner.rb <image> [-l lang]"
  opts.on("-l", "--lang LANG", "Язык OCR") { |l| options[:lang] = l }
end.parse!

image_path = ARGV[0]
unless image_path && File.exist?(image_path)
  puts "❌ Файл не найден: #{image_path}"
  exit 1
end

lang = options[:lang] || 'eng'

puts "\e[36m📄 DocuScan Pro (Ruby)\e[0m"
puts "📂 Обработка: #{image_path}"

start = Time.now

begin
  # Загрузка изображения и поиск контуров (упрощённо)
  img = Magick::Image.read(image_path).first
  ratio = img.rows / 500.0
  resized = img.resize((img.columns / ratio).to_i, 500)

  # Упрощённая обработка: просто преобразуем в градации серого и бинаризуем
  gray = resized.quantize(256, Magick::GRAYColorspace)
  # Имитация обнаружения контуров (упрощённо)
  
  # Сохраняем обработанное изображение
  out_img = image_path.sub(/\.[^.]+$/, '') + '_scanned.jpg'
  gray.write(out_img)

  # OCR
  text = RTesseract.new(out_img, lang: lang).to_s.strip
  elapsed = Time.now - start

  out_txt = image_path.sub(/\.[^.]+$/, '') + '_scanned.txt'
  File.write(out_txt, text)

  puts "\n\e[32mРезультат:\e[0m"
  puts "─" * 50
  puts text.empty? ? "[Текст не распознан]" : text
  puts "─" * 50

  puts "\e[36m📊 Статистика:\e[0m"
  puts "  Время: #{elapsed.round(2)} сек"
  puts "  Слов: #{text.split(/\s+/).reject(&:empty?).size}"
  puts "  Символов: #{text.size}"
  puts "\e[32m💾 Сохранено: #{out_img}\e[0m"
  puts "\e[32m💾 Сохранено: #{out_txt}\e[0m"
rescue => e
  puts "\e[31m❌ Ошибка: #{e.message}\e[0m"
  exit 1
end
