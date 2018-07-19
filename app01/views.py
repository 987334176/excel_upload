import os
import json
import uuid
import xlrd
from app01 import models
from django.contrib import auth
from django.contrib.auth.models import User
from excel_upload import settings
from django.shortcuts import render, HttpResponse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

from utils.code import check_code

def code(request):
    """
    生成图片验证码
    :param request:
    :return:
    """
    img,random_code = check_code()
    request.session['random_code'] = random_code
    from io import BytesIO
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())

# Create your views here.
def login(request):  # 登录
    if request.method == "POST":
        username = request.POST.get("user")
        pwd = request.POST.get("pwd")
        code = request.POST.get('code')
        response = {"state": False}
        if code.upper() != request.session['random_code'].upper():
            response["msg"] = '验证码错误!'
            return HttpResponse(json.dumps(response))
            # return render(request, 'login.html', {'msg': '验证码错误'})
        # 用户验证成功,返回user对象,否则返回None
        user = auth.authenticate(username=username, password=pwd)

        if user:
            # 查询当前用户对象
            user_obj = User.objects.filter(username=username).first()
            # 增加session
            request.session['is_login'] = True
            request.session['user'] = username
            # 更新最后登录时间
            request.session['last_time'] = str(user_obj.last_login)
            user_obj.save()

            # 登录,注册session
            # 全局变量 request.user=当前登陆对象(session中)
            auth.login(request, user)
            # return redirect("/index/")
            response["state"] = True

        response["msg"] = '用户名或者密码错误!'
        return HttpResponse(json.dumps(response))

    return render(request, "login.html")

#装饰器，用来判断用户是否登录
def required_login(func):
    def inner(*args,**kwargs):
        request = args[0]  # 响应请求
        if request.session.get("is_login"): #判断登录状态,如果为True
            return func(*args,**kwargs)  # 执行视图函数
        else:
            if request.is_ajax():  # 此时未登录，判断ajax请求
                #返回一个json信息，并指定url
                return HttpResponse(json.dumps({"state":False,'url':'/login/'}))

            return render(request,"no_login.html")
            #return redirect("/login/")  # 302重定向

    return inner

def logout(request):  # 注销
    auth.logout(request)
    return redirect("/login/")

@required_login
def upload_excel_file(request):  # 上传文件
    if request.method == "GET":
        return render(request, 'upload_excel_file.html')

    user = request.POST.get('user')
    file_upload = request.FILES.get('customer_excel')  # 获取excel文件对象
    # 判断上传的文件后缀
    if file_upload.name.rsplit('.', maxsplit=1)[1] not in ['xls','xlsx']:
        return HttpResponse('上传失败,只能上传xls格式')
    # 生成唯一的文件名
    file_name = str(uuid.uuid4()) + '.' + file_upload.name.rsplit('.', maxsplit=1)[1]
    # 拼接路径
    img_file_path = os.path.join('static', 'files', file_name)
    print(img_file_path)

    with open(img_file_path, 'wb') as f:  # 写入文件
        for line in file_upload.chunks():
            f.write(line)

    # 拼接excel文件的绝对路径
    file_path = os.path.join(settings.BASE_DIR, img_file_path)
    print(file_path)
    # 打开excel表
    data = xlrd.open_workbook(file_path)
    table = data.sheet_by_index(0)  # 读取第一个sheet
    nrows = table.nrows  # 获得总行数
    date_list = []  # 定义空列表，用来批量插入
    try:
        for i in range(1, nrows):  # 读取每一行数据
            rows = table.row_values(i)  # 行的数据放在数组里
            # 生成对象
            obj_list = models.Customer(name=rows[0],
                                       age=rows[1],
                                       email=rows[2],
                                       company=rows[3],

                                       )
            # 追加到列表中
            date_list.append(obj_list)

        # 使用bulk_create批量插入
        models.Customer.objects.bulk_create(date_list)

        # 删除上传的excel文件
        os.remove(file_path)

    except Exception as e:
        return HttpResponse('批量添加失败{}'.format(e))

    return redirect('/index/')  # 跳转首页

@required_login
def index(request):  # 首页展示数据
    customer_list = models.Customer.objects.all()  # 读取表中的所有数据
    # print()
    paginator = Paginator(customer_list, 20)  # 每页显示2条

    # 异常判断
    try:
        # 当前页码，如果取不到page参数，默认为1
        current_num = int(request.GET.get("page", 1))  # 当前页码
        customer_list = paginator.page(current_num)  # 获取当前页码的数据
    except EmptyPage:  # 页码不存在时,报EmptyPage错误
        customer_list = paginator.page(1)  # 强制更新为第一页

    #  如果页数十分多时，换另外一种显示方式
    if paginator.num_pages > 9:  # 一般网页展示11页,左5页,右5页,加上当前页,共11页
        if current_num - 4 < 1:  # 如果前5页小于1时
            pageRange = range(1, 9)  # 页码的列表:范围是初始状态
        elif current_num + 4 > paginator.num_pages:  # 如果后5页大于总页数时
            # 页码的列表:范围是(当前页-5,总页数+1)。因为range顾头不顾尾,需要加1
            pageRange = range(current_num - 4, paginator.num_pages + 1)
        else:
            # 页码的列表:后5页正常时,页码范围是(当前页-5,当前页+6)。注意不是+5,因为range顾头不顾尾！
            pageRange = range(current_num - 4, current_num + 5)
    else:
        pageRange = paginator.page_range  # 页码的列表

    data = {"customer_list": customer_list, "paginator": paginator, "current_num": current_num, "pageRange": pageRange}
    return render(request, "index.html", data)
