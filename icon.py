from PIL import Image

src = Image.open("assets/logo.png")
sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
# optionally use LANCZOS for sharper resizing:
icon_imgs = [src.resize(s, Image.LANCZOS) for s in sizes]
icon_imgs[0].save("assets/icon.ico", sizes=sizes)