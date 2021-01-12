#!/usr/bin/env python
# coding: utf-8


from statsmodels.tsa.ar_model import AR
def AR_error(data,cof):
    #data：误差数据 cof：衰减系数
    # 训练模型得到所需参数：AR的滞后项个数p，和自回归函数的各个系数
    model_fit = AR(data).fit()
    params = model_fit.params
    p = model_fit.k_ar  
    history = data[-p:]   
    history = np.hstack(history).tolist() 
    errors = []
    lag = history[-p:]
    yhat = params[0]
    for i in range(p):
        yhat += params[i+1] * lag[p-1-i]
    for j in range(8):
        errors.append(yhat)
        yhat*=cof
    return errors






