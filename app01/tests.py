from django.test import TestCase

# Create your tests here.
'''
1. iframe标签
    可以修改src，且页面不刷新
2. form表单
    提交表单数据，但刷新数据
'''
import uuid

name = "test_name"
namespace = "test_namespace"

print(uuid.uuid1())  # 带参的方法参见Python Doc
print(uuid.uuid3(namespace, name))
print(uuid.uuid4())
print(uuid.uuid5(namespace, name))