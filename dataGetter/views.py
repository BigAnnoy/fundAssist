from django.shortcuts import render
import efinance as ef
import time
from datetime import datetime
import pandas as pd
import time
from datetime import timedelta
from dataGetter import models
from django.views.decorators.http import require_http_methods
from tabulate import tabulate
import warnings

warnings.filterwarnings("ignore")
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.http import JsonResponse
from django_pandas.io import read_frame


fund_codes=list(models.funds.objects.values_list("fund_code", flat=True))
#["005928","001644","007164","005506","009876","008960","006080","008084","014162","005763"]
#上次数据刷新的时间，数据字典{基金名:数据}，基金组成
data_refresh_last_time=datetime(2000, 1, 1, 15, 30)
data_refresh_latest= {}
data_refresh_last_list=[]

time_dif=60
freq = 5

def data_refresher(request):
    global data_refresh_last_time,data_refresh_latest,data_refresh_last_list
    res = {}
    res["fund_codes"] = list(models.funds.objects.values_list("fund_code", flat=True))
    res["fund_data"] = {}
    if (datetime.today()-timedelta(seconds=60)>data_refresh_last_time) or res["fund_codes"].sort()!=data_refresh_last_list:
        for i in res["fund_codes"]:
            r,res["fund_data"][i]=get_fin_change_weighted(i,freq)
            res["fund_data"][i]=res["fund_data"][i].to_html(classes="table-light")
        data_refresh_latest=res["fund_data"]
        data_refresh_last_time=datetime.today()
        data_refresh_last_list=res["fund_codes"]
        print("满足条件，已经获取实时数据")
    else:
        res["fund_data"]=data_refresh_latest
        print("不满足条件，使用上次数据")
    res["data_refresh_time"]=str(data_refresh_last_time).split('.')[0]
    return JsonResponse(res)

def index(request):
    context={"fund_list_dy":list(models.funds.objects.values_list("fund_code", flat=True))}
    return render(request, "homePage.html",context)



# 获取多个股票的原始数据字典
def get_origin_data(freq, stock_codes):
    origin_data_dict = {}

    data_refresh_time = str(datetime.today()).split('.')[0]
    data_time = str(data_refresh_time).replace(":", ",")
    for stock_code in stock_codes.copy():
        # 现在的时间
        now = str(datetime.today()).split('.')[0]
        # 获取最新一个交易日的分钟级别股票行情数据
        origin_data_dict[str(stock_code)] = ef.stock.get_quote_history(stock_code, klt=freq)
    return data_refresh_time, origin_data_dict


# 转原始数据excel
def trans_to_excel(data_time, dict_all):
    excel_name = "数据获取历史/行情数据获取" + data_time + ".xlsx"
    writer = pd.ExcelWriter(excel_name)
    for k, v in dict_all.items():
        v.to_excel(writer, sheet_name=k)
    writer.close()


# 多个股票的原始数据字典→涨跌幅字典
def get_core_data(origin_data_dict, stock_code):
    single_df = origin_data_dict[stock_code]
    single_df["日期"] = pd.to_datetime(single_df["日期"])
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


# 将多个股票的原始数据字典转为一个涨跌幅dataframe
def conbin_change(origin_data_dict):
    conbin_change = pd.DataFrame()
    for k, v in origin_data_dict.items():
        conbin_change = pd.concat([conbin_change, get_core_data(origin_data_dict, k)], axis=1)
    return conbin_change


# 根据基金编号获取
def get_fin_change_weighted(fund_code, freq):
    fund_cons = ef.fund.get_invest_position(fund_code)
    stock_codes = fund_cons["股票简称"].tolist()
    stock_perc = fund_cons["持仓占比"]
    while True:
        data_refresh_time, origin_data_dict = get_origin_data(freq, stock_codes)
        fin_change = conbin_change(origin_data_dict)
        break
    fin_change_weighted = fin_change
    fin_change_weighted_temp = fin_change * fund_cons.set_index("股票简称")["持仓占比"]
    fin_change_weighted["加权合计"] = fin_change_weighted_temp.apply(lambda x: x.sum(), axis=1)/100
    return data_refresh_time,fin_change_weighted.applymap(lambda x: '%.2f%%' % (x * 100))


# 多基金数据获取并打印
def mult_fund_display(fund_codes, freq):
    for i in fund_codes:
        # displaying the DataFrame
        print("基金编号:" + i)
        print(tabulate(i,get_fin_change_weighted(i, freq).tail(10), headers='keys', tablefmt='pretty'))

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
    print(list(models.funds.objects.values_list("fund_code", flat=True)))
    return HttpResponse(request,)