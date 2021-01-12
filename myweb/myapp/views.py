from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from myapp import models
import numpy as np
import datetime
import xml
from myapp import AR_error
import json
# Create your views here.
#定义展示函数
model=settings.MODEL
cof=0.8 #衰减系数
Arror_flag = False #是否加入自回归校正
 #插入函数
def post(request):
    if request.method == "POST":
        post_data = json.loads(request.body)
        I = post_data.get("I") #光照强度
        T = post_data.get("T") #板温
        P = post_data.get("P") #光伏功率信息
        if(len(I)!=16 or len(T)!=16 or len(P)!=16):
            return HttpResponse('输入错误')
        if Arror_flag:
            error=request.POST.get("error",None)#误差信息
            #需要经过数据处理
        I=fill(I)
        T=fill(T)
        P=fill(P)
        input_x=np.vstack((I,T,P)).T
        print("输入数据大小",input_x.shape)
        input_x=input_x.reshape((1,16,3))#input_x的格式
        print("预测中......") 
        predict=model.predict(input_x, verbose=0)#
        predict=predict.reshape(8,1)
        predict[predict<0]=0
        if Arror_flag:
            predict+=AR_error.AR_error(error,cof)#自回归校正
        print("预测完成")
        path = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
#         print_xml(predict,file="./"+path+".xml")#xml保存地址
        doc = print_xml(predict)#xml保存地址
        print("xml已输出")
        now = (datetime.datetime.now()+datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M")
        twz = models.message.objects.create(I=I[0], T=T[0],Time=now,predict_result=predict[0])
        #objects.create 往数据表中插入内容的方法
        twz.save()
        return HttpResponse(doc, content_type='text/xml')
       
    else:
        return HttpResponse('方法错误')
#数据预处理
def fill(df):
    for i in range(len(df)): 
        df[i] = float(df[i])
        if df[i]==None and i !=0:
            df[i]=df[i-1]
        elif df[i]==None and i==0:
            df[i]=df[i+1]
       
    return df
#定义输出xml函数
def print_xml(df):   
    l=df.shape[0]
    doc = xml.dom.minidom.Document() 
    #创建根节点
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    root = doc.createElement('shortforecast') 
    root.setAttribute('stationId', 'xxx')
    root.setAttribute('type','CDQ')
    root.setAttribute('time','')
    root.setAttribute('createTime',now)
    root.setAttribute('capacity','20')
    doc.appendChild(root)
    #创建data子节点
    for i in range(l):
        objectdata = doc.createElement("data")

        objectid = doc.createElement("id")
        objectidtext = doc.createTextNode(str(i))
        objectid.appendChild(objectidtext)
        objectdata.appendChild(objectid)

        objecttime = doc.createElement("time")
        T = (datetime.datetime.now()+datetime.timedelta(minutes=15*(i+1))).strftime("%Y-%m-%d %H:%M")
        objecttimetext = doc.createTextNode(T)
        objecttime.appendChild(objecttimetext)
        objectdata.appendChild(objecttime)

        objectP_ALL= doc.createElement("P_ALL")
        objectP_ALLtext = doc.createTextNode(str(df[i]))
        objectP_ALL.appendChild(objectP_ALLtext)
        objectdata.appendChild(objectP_ALL)

        objectunitlist = doc.createElement("unitList")
        # objectunitlisttext = doc.createTextNode(str("df.iloc[i,1]"))
        # objectunitlist.appendChild(objectunitlisttext)

        objectunit1 = doc.createElement("unit")

        objectunit1name = doc.createElement("name")
        objectunit1nametext = doc.createTextNode(str("P_001"))
        objectunit1name.appendChild(objectunit1nametext)
        objectunit1.appendChild(objectunit1name)

        objectunit1value = doc.createElement("value")
        objectunit1valuetext = doc.createTextNode(str(df[i]))
        objectunit1value.appendChild(objectunit1valuetext)
        objectunit1.appendChild(objectunit1value)

        objectunitlist.appendChild(objectunit1)
#不需要P_002的输出
#         objectunit2 = doc.createElement("unit")

#         objectunit2name = doc.createElement("name")
#         objectunit2nametext = doc.createTextNode(str("P_002"))
#         objectunit2name.appendChild(objectunit2nametext)
#         objectunit2.appendChild(objectunit2name)

#         objectunit2value = doc.createElement("value")
#         objectunit2valuetext = doc.createTextNode(str(df.iloc[i,0]))
#         objectunit2value.appendChild(objectunit2valuetext)
#         objectunit2.appendChild(objectunit2value)

#         objectunitlist.appendChild(objectunit2)

        objectdata.appendChild(objectunitlist)
        root.appendChild(objectdata)
#     f = open(f'{file}', 'w')
#     doc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
#     f.close()
    return doc.toxml()
