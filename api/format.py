import cv2
import os
import moviepy.editor as mpy
import io
from PIL import Image, ImageSequence
from moviepy.editor import ImageSequenceClip
import tinify
from PIL.Image import EXTENT
import imageio

API_key = "kJzWK7rTvfy40scDSRfs0j61Bx2rryMh"
tinify.key = API_key
def get_size(file, form, is_path=False):
    # 获取文件大小:KB
    if is_path:
        size = os.path.getsize(file)/1024
    else:
        imgByteArr = io.BytesIO()
        file.save(imgByteArr, format=form)
        imgByteArr = imgByteArr.getvalue()
        size = len(imgByteArr)/1024
    print("size:", size)
    return size

def compress_core(img, out_path, form, mb):
    img.save(out_path, form=form)
    o_size = get_size(img, form)
    if o_size <= mb:
        img.save(out_path)
    while o_size > mb:
        source = tinify.from_file(out_path)  # 压缩指定文件
        source.to_file(out_path)  # 将压缩后的文件输出当指定位置
        o_size = get_size(out_path, form, is_path=True)
    return True


def compress_image(img, out_path,form='gif', mb=150, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    """
    o_size = get_size(img, form)
    if o_size <= mb:
        img.save(out_path)
    while o_size > mb:
        img.save(out_path, format=form, quality=quality)
        if quality - step < 0:
            return False
        quality -= step
        o_size = get_size(out_path, form, is_path=True)
        img = Image.open(out_path)
    return True

def change2square(img,w,h):
    img_width = img.size[0]
    img_height = img.size[1]
    if img.size[0] > img.size[1]:
        rate = h / img_height
        img = img.resize((int(img_width * rate), h))
        offset = int(img.size[0] - w) / 2
        img = img.crop((offset, 0, w + offset, h))
    else:
        rate = w / img_width
        img = img.resize((w, int(img_height * rate)))
        # print(img.size)
        offset = int(img.size[1] - h) / 2
        img = img.crop((0, offset, w, h + offset))
        # print(img.size)
    return img

def change_aspect_rate(img, w, h):
    img_width = img.size[0]
    img_height = img.size[1]
    if (img_width / img_height) > (w / h): #crop w
        rate =  h / img_height
        img = img.resize((int(img_width * rate), h))
        offset = int(img.size[0] - w) / 2
        img = img.crop((offset, 0, w+offset, h))
    else:#crop h
        rate = w / img_width
        img = img.resize((w, int(img_height*rate)))
        # print(img.size)
        offset = int(img.size[1] - h) / 2
        img = img.crop((0, offset, w, h+offset))
        # print(img.size)
    return img

def process_img(inputfile_path, savefile_path, w, h,  form, mb):
    img = Image.open(inputfile_path)
    if w == h:
        img = change2square(img, w, h)
    else:
        img = change_aspect_rate(img, w, h)
    if_sucess = compress_core(img, savefile_path, form=form, mb=mb)
    # if if_sucess is False:
    print(inputfile_path, if_sucess)

def process_dir(input_path, save_dir, w,h, mb, form, is_vedio=False):
    i = 1
    for img_file_path in os.listdir(input_path):
        if not (img_file_path.__contains__("detail") or img_file_path.__contains__("cover") or img_file_path.__contains__("chat")):
            if is_vedio:
                vedio2gif(input_path + img_file_path, save_dir + "{}.{}".format(str(i).zfill(2), form), w, h, form, mb)
            else:
                process_img(input_path + img_file_path, save_dir + "{}.{}".format(str(i).zfill(2), form), w, h, form=form, mb=mb)
            i += 1

def vedio2gif(inputfile_path, savefile_path, w, h,form, mb):
    cmd="ffmpeg -i {} -vf scale={}:-1 -r 8 -b:v 200k  {} ".format(inputfile_path, w, savefile_path)
    print(cmd)
    os.system(cmd)

    im = Image.open(savefile_path)
    # GIF图片流的迭代器
    iter = ImageSequence.Iterator(im)
    dur = (im.info)['duration'] / 1000
    index = 1
    # 遍历图片流的每一帧
    for frame in iter:
        print("image %d: mode %s, size %s" % (index, frame.mode, frame.size))
        if w == h:
            frame = change2square(frame, w, h)
        else:
            frame = change_aspect_rate(frame, w, h)
        # if index%3 == 0:
        frame = frame.convert('RGB')
        if_sucess = compress_core(frame, "temp_{}.png".format(index), form="png", mb=mb/25)
        index += 1
    # 把图片流重新成成GIF动图
    print(index)
    images = []
    for i in range(1, index):
        # if i % 3 == 0:
        images.append(imageio.imread("temp_{}.png".format(i)))
    imageio.mimsave(savefile_path, images, duration=dur)
    # img = Image.open(savefile_path)
    # if_sucess = compress_core(img, savefile_path, form=form, mb=mb)
    # if if_sucess is False:
    # print(inputfile_path, if_sucess)

if __name__ == '__main__':
    input_path = "/home/weishu/disk/Pic/wechat/vedio/"
    output_path = "/home/weishu/disk/Pic/wechat/vedio_output/"
    os.system("mkdir -p {}".format(output_path))
    sample = 0.95
    process_dir(input_path, output_path, 240, 240, mb=500*sample, form="gif", is_vedio=True) #表情主图
    # process_dir(input_path, output_path, 240, 240, mb=500*sample, form="gif") #表情主图
    # process_dir(input_path, output_path, 120, 120, mb=50*sample, form="png") #表情缩略图，表情专辑
    # process_img(input_path+"detail.jpeg", output_path+"detail.png", 750, 400, mb=80*sample, form="png") #表情封面图
    # process_img(input_path+"cover.jpeg", output_path+"cover.png", 240, 240, mb=80*sample, form="png") #表情封面图
    # process_img(input_path+"chat.jpeg", output_path+"chat.png", 50, 50, mb=30*sample, form="png") #聊天面板图标
    # process_img(input_path+"follow.jpeg", output_path+"follow.png", 750, 560, mb=100*sample, form="png") #引导图图标
    # process_img(input_path+"thank.jpeg", output_path+"thank.png", 750, 750, mb=200*sample, form="png") #致谢图标
