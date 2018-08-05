本程序运行环境：python3.5.4,django 2.0,7
说明：
excel文件上传
数据库使用的是sqlite

首页路径为/index/
目前实现的功能如下

1. 登录页面 /login/  基于ajax
2. 不能直接访问后台页面，必须要登录。否则会有弹框提示！
3. 登陆之后，访问/upload_file/ 进行excel文件上传

运行方式：使用Pycharm直接运行即可。
或者使用命令
python manage.py runserver

默认管理员账号xiao
密码123456
