from PIL import Image

def convert_png_to_ico(source_file, target_file):
    # 打开 PNG 图片
    img = Image.open(source_file)
    
    # 确保图片是 RGBA 模式 (保证透明度)
    img = img.convert("RGBA")
    
    # 定义标准 ICO 包含的尺寸（包含高清 256px）
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 保存为 ICO
    img.save(target_file, sizes=icon_sizes)
    print(f"成功生成透明 ICO: {target_file}")

if __name__ == "__main__":
    # 请确保你已经把上面生成的图片保存为 app_icon.png
    convert_png_to_ico('app_icon.png', 'app_icon.ico')