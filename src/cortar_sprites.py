import os
import sys
from PIL import Image

def slice_sprites():
    # Detecta la raíz del proyecto (un nivel arriba de src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    grid_path = os.path.join(assets_dir, "ayeon_expresiones-3.jpg")

    if not os.path.exists(grid_path):
        print(f"[ERROR] No se encontro el archivo: {grid_path}")
        sys.exit(1)

    layout = [
        ["feliz", "zen", "agotada"],
        ["triste", "concentrada", "cafe"],
        ["eureka", "enamorada", "enojada"]
    ]

    try:
        with Image.open(grid_path) as img:
            width, height = img.size
            cell_w = width // 3
            cell_h = height // 3

            print(f"Dimensiones: {width}x{height} px | Celda: {cell_w}x{cell_h} px")

            for r in range(3):
                for c in range(3):
                    name = layout[r][c]
                    box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
                    cropped = img.crop(box)
                    
                    out_path = os.path.join(assets_dir, f"{name}.png")
                    cropped.save(out_path, format="PNG")
                    print(f"OK: assets/{name}.png")

        print("\n[EXITO] Los 9 sprites fueron procesados correctamente.")

    except Exception as e:
        print(f"[ERROR] Fallo al procesar la imagen: {e}")
        sys.exit(1)

if __name__ == "__main__":
    slice_sprites()
