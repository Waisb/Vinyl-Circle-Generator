import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import VideoClip, AudioFileClip

# Вырезка круга из изображения
def crop_circle(im, size):
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    im = im.resize((size, size), resample=Image.LANCZOS).convert('RGBA')
    im.putalpha(mask)
    return im

# Изменение прозрачности (для всего)
def adjust_opacity(im, alpha=1.0):
    assert 0 <= alpha <= 1
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')

# Основная функция генерации кружков
def make_rotating_vinyl_mp4(
    disk_path, # путь до изображения диска
    label_path, # путь до изображения
    audio_path, # путь до аудио
    output_path, # выходное название файла
    shine_path=None, # путь до изображения переднего слоя (опционально)
    shine_opacity=1.0, # прозрачность переднего слоя
    shine_rotate=False, # вращается ли передний слой (по умолчанию True)
    center_shadow_path=None, # путь до изображения центральной тени (опционально)
    center_shadow_opacity=1.0, # прозрачность центральной тени
    label_opacity=1.0, # прозрачность изображения
    size=300, # размер диска (по умолчанию 300 для телеграмма)
    label_size=180, # размер изображения (подбирать под диск)
    rotation_speed=33, # скорость вращения диска
    fps=30, # частота кадров (по умолчанию 30)
    bitrate="10000k", # битрейт (по умолчанию 10000k)
    center_hole_radius=None, # радиус центрального отверстия (опционально)
    ffmpeg_logs = False # логирование ffmpeg (по умолчанию False)

):
    """
    disk_path - путь до изображения диска
    label_path - путь до изображения
    audio_path - путь до аудио
    output_path - выходное название файла
    shine_path - путь до изображения переднего слоя (опционально)
    shine_opacity - прозрачность переднего слоя
    shine_rotate - вращается ли передний слой (по умолчанию True)
    center_shadow_path - путь до изображения центральной тени (опционально)
    center_shadow_opacity - прозрачность центральной тени
    label_opacity - прозрачность изображения
    size - размер диска (по умолчанию 300 для телеграмма)
    label_size - размер изображения (подбирать под диск)
    rotation_speed - скорость вращения диска
    fps - частота кадров (по умолчанию 30)
    bitrate - битрейт (по умолчанию 10000k)
    center_hole_radius  - радиус центрального отверстия (опционально)
    ffmpeg_logs - логирование ffmpeg (по умолчанию False)
    """

    # Загрузка слоёв и подготовка
    disk = Image.open(disk_path).convert("RGBA").resize((size, size), resample=Image.LANCZOS)
    label_img = Image.open(label_path).convert("RGBA")
    label = crop_circle(label_img, label_size)
    if label_opacity < 1.0:
        label = adjust_opacity(label, label_opacity)
    # Передний слой (световой например)
    if shine_path:
        shine = Image.open(shine_path).convert("RGBA").resize((size, size), resample=Image.LANCZOS)
        shine = adjust_opacity(shine, shine_opacity)
    else:
        shine = None
    # Наложение центрального слоя (например центральная тень)
    if center_shadow_path:
        shadow_size = int(label_size * 1.18)
        center_shadow = Image.open(center_shadow_path).convert("RGBA").resize((shadow_size, shadow_size), resample=Image.LANCZOS)
        center_shadow = adjust_opacity(center_shadow, center_shadow_opacity)
    else:
        center_shadow = None
    # Аудио и длительность аудио (она жи длительность кружка)
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Генератор кадров
    def make_frame(t):
        angle = (-t * rotation_speed * 360 / 60) % 360
        base = disk.copy()
        x = (size - label_size) // 2
        y = (size - label_size) // 2
        base.alpha_composite(label, (x, y))
        # Поворот диска с лейблом
        rotated = base.rotate(angle, resample=Image.BICUBIC, expand=True)
        crop_rotated = rotated.crop((
            (rotated.width - size)//2,
            (rotated.height - size)//2,
            (rotated.width + size)//2,
            (rotated.height + size)//2
        ))
        # Тень центра (не вращается)
        if center_shadow is not None:
            sh = center_shadow
            sx = (size - sh.width) // 2
            sy = (size - sh.height) // 2
            crop_rotated.alpha_composite(sh, (sx, sy))
        # Передний слой: вращающийся или нет
        if shine is not None:
            if shine_rotate:
                rotated_shine = shine.rotate(angle, resample=Image.BICUBIC, expand=True)
                sx = (rotated_shine.width - size) // 2
                sy = (rotated_shine.height - size) // 2
                rotated_shine_cropped = rotated_shine.crop((sx, sy, sx+size, sy+size))
                crop_rotated.alpha_composite(rotated_shine_cropped, (0, 0))
            else:
                crop_rotated.alpha_composite(shine, (0, 0))
        # Вырез по центру (may not work!)
        if center_hole_radius:
            if isinstance(center_hole_radius, float) and center_hole_radius < 1:
                hole_r = int(size * center_hole_radius)
            else:
                hole_r = int(center_hole_radius)
            mask = Image.new('L', (size, size), 255)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (
                    (size - 2*hole_r)//2,
                    (size - 2*hole_r)//2,
                    (size + 2*hole_r)//2,
                    (size + 2*hole_r)//2
                ),
                fill=0
            )
            crop_rotated.putalpha(mask)
        return np.array(crop_rotated.convert('RGB'))

    # Создание и запись видео
    video = VideoClip(make_frame, duration=duration).set_audio(audio).set_fps(fps)
    video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=fps,
        bitrate=bitrate, # Больше = лучше. При значениях меньше 10000k множественные пиксели
        preset='veryslow', # Важно, из-за этого возникала проблема с кодировкой и генерировало бред
        logger=None if ffmpeg_logs == False else 'bar',
        ffmpeg_params=["-pix_fmt", "yuv420p", "-profile:v", "high"] #Важно, из-за этого возникала проблема с кодировкой и генерировало бред
    )
    # Возврат пути до итогового файла 
    return output_path


# Пример использования
# make_rotating_vinyl_mp4(
#     disk_path="disk.png",
#     label_path="label.jpg",
#     audio_path="audio.mp3",
#     output_path="vinyl.mp4",
#     shine_path="shine.png",
#     shine_opacity=0.5,
#     shine_rotate=False,
#     center_shadow_path="shadow.png",
#     center_shadow_opacity=0.6,
#     label_opacity=0.85,
#     size=300,
#     label_size=120,
#     rotation_speed=10,
#     fps=30,
#     bitrate="12000k",
#     center_hole_radius=0.8 
# )
