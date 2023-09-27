import json

from django.shortcuts import render
import efinance as ef
from datetime import datetime
import pandas as pd
from datetime import timedelta
from dataGetter import models

import warnings

warnings.filterwarnings("ignore")
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.http import JsonResponse


fund_codes=list(models.funds.objects.values_list("fund_code", flat=True))
#["005928","001644","007164","005506","009876","008960","006080","008084","014162","005763"]
#上次数据刷新的时间，数据字典{基金名:数据}，基金组成


time_dif=60
freq = 5

def data_refresher(request):
    res = {}
    res["fund_codes"] = list(models.funds.objects.values_list("fund_code", flat=True))
    res["fund_data"] = {}
    begin_time=str(datetime.today().date()-timedelta(days=3)).replace("-","")
    print("数据抓取开始"+str(datetime.today()))
    for i in res["fund_codes"]:
        res["fund_data"][i]=get_fin_change_weighted(i,freq,begin_time)
        res["fund_data"][i]=res["fund_data"][i].to_html(classes="table-light")
    print("满足条件，已经获取实时数据"+str(datetime.today()))
    res["data_refresh_time"]=str(datetime.today()).split('.')[0]
    #conn = get_redis_connection()
    #conn.set("data", json.dumps(data_refresh_latest))
    #json.loads
    return JsonResponse(res)

def index(request):
    context={"fund_list_dy":list(models.funds.objects.values_list("fund_code", flat=True))}
    return render(request, "homePage.html",context)



# 获取多个股票的原始数据字典
def get_origin_data(freq, stock_codes,begin_time):
    origin_data_dict= ef.stock.get_quote_history(stock_codes, klt=freq,beg=begin_time)
    return  origin_data_dict


# 转原始数据excel
def trans_to_excel(data_time, dict_all):
    excel_name = "数据获取历史/行情数据获取" + data_time + ".xlsx"
    writer = pd.ExcelWriter(excel_name)
    for k, v in dict_all.items():
        v.to_excel(writer, sheet_name=k)
    writer.close()


# 多个股票的原始数据字典→涨跌幅
def get_core_data(single_df, stock_code):
    single_df["日期"]=pd.to_datetime(single_df["日期"])
    single_df_last=pd.DataFrame()
    last_deal_time=datetime.today().date()
    while len(single_df_last)==0:
        single_df_last=single_df[single_df["日期"].dt.date == last_deal_time]
        last_deal_time=last_deal_time-timedelta(1)
    single_df_last_close = single_df[single_df["日期"].dt.date != (last_deal_time+timedelta(1))].iloc[-1, :, ]
    real_time_change = single_df_last[["日期", "收盘"]]
    real_time_change[stock_code] = real_time_change["收盘"] / single_df_last_close['收盘'] - 1
    real_time_change = real_time_change.drop("收盘", axis=1)
    real_time_change = real_time_change.set_index("日期")
    return real_time_change


# 将多个股票的原始数据字典，计算涨跌幅
def conbin_change(origin_data_dict):
    conbin_change = pd.DataFrame()
    for k, v in origin_data_dict.items():
        conbin_change = pd.concat([conbin_change, get_core_data(v, k)], axis=1)
    return conbin_change


# 根据单个基金编号获取
def get_fin_change_weighted(fund_code, freq, begin_time):
    #获取持仓占比
    fund_cons = ef.fund.get_invest_position(fund_code)
    stock_codes = fund_cons["股票简称"].tolist()
    #获取基金下，多个股票的原始数据
    origin_data_dict = get_origin_data(freq, stock_codes,begin_time)
    #将原始数据转化为涨幅df
    fin_change_weighted = conbin_change(origin_data_dict)
    fin_change_weighted_temp = fin_change_weighted * fund_cons.set_index("股票简称")["持仓占比"]
    col_temp=fin_change_weighted.columns.tolist()
    col_temp.insert(0,"加权合计")
    fin_change_weighted=fin_change_weighted.reindex(columns=col_temp)
    fin_change_weighted["加权合计"] = fin_change_weighted_temp.apply(lambda x: x.sum(), axis=1)/100
    return fin_change_weighted.applymap(lambda x: '%.2f%%' % (x * 100))

def add_fund(request):
    fund_code=request.POST.get("fundcode")
    fund_code_zh=ef.fund.get_base_info([fund_code])["基金简称"][0]
    models.funds.objects.create(fund_code=fund_code,fund_code_zh=fund_code_zh)
    flist = models.funds.objects.all().values()
    return render(request,"fundManage.html",{"fund_list":flist})

def  del_fund(request,fund_code):
    models.funds.objects.get(fund_code=fund_code).delete()
    flist = models.funds.objects.all().values()
    return render(request, "fundManage.html", {"fund_list": flist})

def fund_list(request):
    flist = models.funds.objects.all().values()
    return  render(request,"fundManage.html",{"fund_list":flist})

def print_info(request):

    return HttpResponse(request)