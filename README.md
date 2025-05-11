
# Генератор виниловых кружочков для социальных сетей

Код позвляющий создавать виниловые кружочки с возможностью модификации всех параметров.

#### Параметры создания
```python
  make_rotating_vinyl_mp4
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `disk_path` | `string` | **Required**. Путь до картинки с диском. |
| `label_path` | `string` | **Required**. Путь до картинки внутри/вне диска. |
| `audio_path` | `string` | **Required**. Путь до звука на видео. |
| `output_path` | `string` | **Required**. Название файла на выходе. |
| `shine_path` | `string` | *Optional*. Путь до накладываемого эффекта. |
| `shine_opacity` | `float` | *Optional*. Уровень прозрачности накладываемого эффекта. |
| `shine_rotate` | `bool` | *Optional*. Должен ли вращаться накладываемый эффект. |
| `center_shadow_path` | `string` | *Optional*. Путь до изображения центрального эффекта. |
| `center_shadow_opacity` | `float`| *Optional*. Прозрачность центрального эффекта. |
| `label_opacity` | `float` | *Optional*. Прозрачность картинки внутри/вне диска. |
| `size` | `int` | *Optional*. Размер диска |
| `label_size` | `int` | *Optional*. Прозрачность картинки внутри/вне диска. |
| `rotation_speed` | `int` | *Optional*. Скорость вращения диска. |
| `fps` | `int` | *Optional*. FPS выходного видео. |
| `bitrate` | `string` | *Optional*. Битрейт рендера. |
| `center_hole_radius` | `int` | *Optional*. Радиус центрального отверстия. |
| `ffmpeg_logs` | `bool` | *Optional*. Отображать логи работы ffmpeg. |


## Пример создания

```python
make_rotating_vinyl_mp4(
    disk_path="disk.png",
    label_path="label.jpg",
    audio_path="audio.mp3",
    output_path="vinyl.mp4",
    shine_path="shine.png",
    shine_opacity=0.5,
    shine_rotate=False,
    center_shadow_path="shadow.png",
    center_shadow_opacity=0.6,
    label_opacity=0.85,
    size=300,
    label_size=120,
    rotation_speed=10,
    fps=30,
    bitrate="12000k",
    center_hole_radius=0.8
)
```


## Итог
![App Screenshot](https://imgur.com/a/Hklvd2q)
