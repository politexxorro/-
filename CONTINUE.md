# Как продолжить проект самому

Всё состояние проекта лежит в репозитории: правила (`RULES.md`), паспорт героев (`characters/CHARACTER_BIBLE.md`),
журнал (`PROGRESS.md`), все рисунки, скрипты и звук.

## 1. Окружение
```bash
pip install requests numpy pillow opencv-python-headless
# ffmpeg с libass (для субтитров)
# Rhubarb Lip Sync 1.13 (липсинк): https://github.com/DanielSWolf/rhubarb-lip-sync/releases
```

## 2. Ключ API (НЕ коммитить!)
Скрипты читают ключ и адрес из файлов в домашней папке:
```bash
mkdir -p ~/.secrets
printf '%s' 'ВАШ_КЛЮЧ_INFARMODEL' > ~/.secrets/infar_key
printf '%s' 'https://infarmodel.com' > ~/.secrets/infar_base
```
Модели на ключе: `gpt-image-2.6-sunburst` (картинки), `eleven_multilingual_v2` (голос).

## 3. Основные скрипты
| Скрипт | Что делает |
|---|---|
| `scripts/api.py` | клиент API: правка картинки по референсам (`edit`), генерация, озвучка |
| `scripts/gen_jobs.py jobs.json N` | пакетная генерация картинок из json (существующие файлы не перезаписывает) |
| `scripts/face_kit.py` | вырезает части лица (глаза/рот) из вариантов рисунка → `characters/face_kit/` |
| `scripts/remove_mole.py` | убирает родинку девушки с готовых рисунков |
| `scripts/split_sheet.py` | режет лист фаз на отдельные фазы |
| `scripts/make_voices.py` | озвучка всех реплик + липсинк Rhubarb |
| `scripts/anim.py` | 2D-композитор: деформации, свет, лучи, пылинки, финальный грейд |
| `shots/shotNN/sceneNN.py` | сборка сцены покадрово → mp4 (`--stills` — сохранить кадры) |

## 4. Пример: пересобрать сцену 1
```bash
python3 shots/shot01/scene01.py --out shots/shot01/render/shot01_picture_v2.mp4
ffmpeg -i shots/shot01/render/shot01_picture_v2.mp4 -i audio/mix/shot01_mix_v1.wav \
  -vf "ass=shots/shot01/subtitles.ass:fontsdir=fonts" -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -c:a aac -shortest shots/shot01/render/shot01_test_v2.mp4
```
