"""
Script para generar los íconos PNG de la PWA.
Ejecutar: python3 generar_iconos.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def crear_icono(size):
    img = Image.new('RGB', (size, size), color='#0077b6')
    draw = ImageDraw.Draw(img)

    m = size / 512  # factor de escala

    # Fondo circular
    draw.ellipse([0, 0, size-1, size-1], fill='#0077b6')

    # Frontón dorado (triángulo)
    pts = [(int(136*m), int(220*m)), (int(256*m), int(130*m)), (int(376*m), int(220*m))]
    draw.polygon(pts, fill='#ffd166')

    # Cuerpo del edificio
    draw.rectangle([int(156*m), int(220*m), int(356*m), int(378*m)], fill='white')

    # Columnas
    for x in [176, 214, 280, 318]:
        draw.rectangle([int(x*m), int(230*m), int((x+18)*m), int(378*m)], fill='#cce7f5')

    # Puerta
    draw.rectangle([int(232*m), int(300*m), int(280*m), int(378*m)], fill='#0077b6')
    draw.ellipse([int(232*m), int(282*m), int(280*m), int(318*m)], fill='#0077b6')

    # Ventanas
    draw.rectangle([int(182*m), int(250*m), int(212*m), int(280*m)], fill='#0077b6')
    draw.rectangle([int(300*m), int(250*m), int(330*m), int(280*m)], fill='#0077b6')

    # Escalones dorados
    draw.rectangle([int(136*m), int(378*m), int(376*m), int(390*m)], fill='#ffd166')
    draw.rectangle([int(116*m), int(390*m), int(396*m), int(402*m)], fill='#ffd166')

    # Mástil
    draw.rectangle([int(250*m), int(90*m), int(254*m), int(132*m)], fill='#ffd166')
    draw.rectangle([int(254*m), int(90*m), int(282*m), int(108*m)], fill='#ffd166')

    return img

output_dir = 'Municipio/static/assets/img'
os.makedirs(output_dir, exist_ok=True)

for size in [192, 512]:
    img = crear_icono(size)
    path = f'{output_dir}/icon-{size}.png'
    img.save(path, 'PNG')
    print(f'✅ Generado: {path}')

print('Listo.')
