# Елизавета Антипова

Сайт-визитка и дизайн двусторонней визитки бизнес-аналитика.

Сайт: https://ryzenovod.github.io/cv_bi/

## Сайт

Обычные HTML и CSS, без сборки и сторонних скриптов. Шрифты и фото хранятся в репозитории. Контакты работают без JavaScript; контакт можно сохранить в адресную книгу через VCF.

Локальный просмотр:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

После push в `main` workflow `Publish website` публикует только `index.html`, `styles.css` и `assets/`. Макеты и служебные инструкции не входят в сайт.

Контент, даты и результаты работы взяты из предоставленного `elizaveta-updated-preview.html`. Ссылки Telegram и VK добавлены по предоставленному скриншоту. Новые места работы, квалификации и показатели не добавлялись.

## Визитка

- `output/pdf/business-card-print-bleed-3mm.pdf` — две страницы, лицо и оборот; размер страницы 96 × 56 мм, TrimBox 90 × 50 мм, вылеты 3 мм.
- `output/pdf/business-card-90x50.pdf` — две стороны в обрезном размере, для согласования.
- `output/pdf/gold-foil-mask-bleed-3mm.pdf` — отдельная векторная маска змеи, 100% K, в тех же координатах, для согласования тиснения.
- `design/card-front.svg`, `design/card-back.svg` — текст в кривых, шрифты не нужны.
- `design/*-editable.svg` — редактируемый текст. Шрифты Cormorant Garamond Medium и Manrope Regular находятся в `assets/fonts/`, лицензии OFL рядом.
- `design/card-front.png`, `design/card-back.png` — изображения 300 dpi.
- `design/qr-site.svg`, `design/qr-site.png` — QR на сайт, коррекция Q, свободное поле 4 модуля.

Параметры для типографии: [design/PRINT.md](design/PRINT.md).

Сборка макетов:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_cards.py
```

Проверка QR на macOS, в том числе на отрендерированном обороте PDF:

```sh
swift scripts/check_qr.swift design/qr-site.png design/card-back.png
```

## Передача владельцу

До передачи необходимо сохранить работу напечатанного QR. Порядок описан в [HANDOVER.md](HANDOVER.md). Передача сейчас не выполнялась: нужен аккаунт получателя и его согласие принять репозиторий.
