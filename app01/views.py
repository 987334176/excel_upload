import os
import json
import uuid
from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def index(request):
    if request.method == "GET":
        return render(request,'index.html')
    user = request.POST.get('user')
    # 获取文件对象,必须使用request.FILES.get
    avatar = request.FILES.get('avatar')
    print(user)
    print(avatar,type(avatar))
    print(avatar.__dict__)  # 查看对象所有属性
    # 文件存储的绝对路径
    path = os.path.join("static", "upload", avatar.name)
    with open(path,'wb') as f:
        # 将大文件分割成若干小文件处理，处理完每个小文件后释放该部分内存
        for line in avatar.chunks():
            f.write(line)  # 写入文件

    return HttpResponse('上传成功')

def upload_file(request):
    if request.method == "GET":
        return render(request, 'upload_file.html')

    # 直接获取图片地址即可，因为ajax已经将图片上传了
    avatar = request.POST.get('avatar')
    user = request.POST.get('user')

    print(avatar,user)
    return HttpResponse("上传成功")

def form_data_upload(request):
    """
    ajax上传文件
    :param request:
    :return:
    """
    img_upload = request.FILES.get('img_upload')  # 获取文件对象
    # 生成随机文件名
    file_name = str(uuid.uuid4()) + "." + img_upload.name.rsplit('.', maxsplit=1)[1]
    # 文件保存到static下的upload目录
    img_file_path = os.path.join('static', 'upload', file_name)
    with open(img_file_path, 'wb') as f:  # 写入问题
        for line in img_upload.chunks():
            f.write(line)
    # 因为ajax发送的图片路径的static前面没有带/，所以这里要拼接一下
    return HttpResponse(os.path.join("/",img_file_path))

def iframe_upload_img(request):
    if request.method == "GET":
        return render(request,'iframe_upload_img.html')

    USER_LIST = []  # 空列表
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    avatar = request.POST.get('avatar')
    # 最加到列表中
    USER_LIST.append(
        {
            'user':user,
            'pwd':pwd,
            'avatar':avatar
        }
    )
    return HttpResponse("上传成功")

def upload_iframe(request):  # iframe post提交
    ret = {'status':True,'data':None}
    try:
        avatar = request.FILES.get('avatar')
        file_name = str(uuid.uuid4()) + "." + avatar.name.rsplit('.', maxsplit=1)[1]
        img_file_path = os.path.join('static', 'upload', file_name)
        with open(img_file_path, 'wb') as f:
            for line in avatar.chunks():
                f.write(line)
        ret['data'] = os.path.join("/",img_file_path)

    except Exception as e:
        ret['status'] = False
        ret['error'] = '上传失败'

    return HttpResponse(json.dumps(ret))