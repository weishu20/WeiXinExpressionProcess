from removebg import RemoveBg
rmbg = RemoveBg("W82pbKL7J4uw3pbrtvegALjh", "error.log") # 引号内是你获取的API
import os
path= ""
files = os.listdir(path)
for file in files:
    rmbg.remove_background_from_img_file(path+file)  # 图片地址
