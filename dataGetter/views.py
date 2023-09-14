from django.shortcuts import render
import efinance as ef
import time
from datetime import datetime
import pandas as pd
import time
from datetime import timedelta

from django.views.decorators.http import require_http_methods
from tabulate import tabulate
import warnings
warnings.filterwarnings("ignore")
#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
# Create your views here.
from django.http import HttpResponse, JsonResponse

def data_refresher(request):
    fund_codes = ["005928", "000001"]
    freq = 5
    mult_fund_display(fund_codes, freq)
    JsonResponse(request)

def index(request):
    fund_codes = ["005928", "000001"]
    freq = 5
    #mult_fund_display(fund_codes, freq)
    return render(request,"homePage.html")

#测试ajax
@require_http_methods(["GET", "POST"])
def test_ajax(request):
    print("41")
    res = {"code": 101, "msg": "请求无效"}
    rest = request.POST
    s1 = int(rest.get("con1"))
    s2 = int(rest.get("con2"))
    s3 = s1 + s2
    res["msg"] = s3
    return JsonResponse(res)

def dataUpDate(request):
    return render(request)



# 获取多个股票的原始数据字典
def get_origin_data(freq,stock_codes):
    origin_data_dict={}
    data_time=str(datetime.today()).split('.')[0]
    data_time=str(data_time).replace(":",",")
    for stock_code in stock_codes.copy():
            # 现在的时间
            now = str(datetime.today()).split('.')[0]
            # 获取最新一个交易日的分钟级别股票行情数据
            origin_data_dict[str(stock_code)]= ef.stock.get_quote_history(stock_code, klt=freq)
            # print(f'已在 {now}, 完成股票: {stock_code} 的行情数据获取')
    return data_time,origin_data_dict

#转原始数据excel
def trans_to_excel(data_time,dict_all):
    excel_name="数据获取历史/行情数据获取"+data_time+".xlsx"
    writer = pd.ExcelWriter(excel_name)
    for k,v in dict_all.items():
            v.to_excel(writer, sheet_name=k)
    writer.close()

#多个股票的原始数据字典→涨跌幅字典
def get_core_data(origin_data_dict,stock_code):
    single_df=origin_data_dict[stock_code]
    single_df["日期"]=pd.to_datetime(single_df["日期"])
    single_df_today=single_df[single_df["日期"].dt.date==datetime.today().date()]
    single_df_last_close=single_df[single_df["日期"].dt.date!=(datetime.today().date())].iloc[-1,:,]
    real_time_change=single_df_today[["日期","收盘"]]
    real_time_change[stock_code]=real_time_change["收盘"]/single_df_last_close['收盘']-1
    real_time_change=real_time_change.drop("收盘",axis=1)
    real_time_change=real_time_change.set_index("日期")
    return real_time_change

#将多个股票的原始数据字典转为一个涨跌幅dataframe
def conbin_change(origin_data_dict):
    conbin_change=pd.DataFrame()
    for k,v in origin_data_dict.items():
        conbin_change=pd.concat([conbin_change,get_core_data(origin_data_dict,k)],axis=1)
    return conbin_change





# 根据基金编号获取
def get_fin_change_weighted(fund_code, freq):
    fund_cons = ef.fund.get_invest_position(fund_code)
    stock_codes = fund_cons["股票简称"].tolist()
    stock_perc = fund_cons["持仓占比"]
    while True:
        data_time, origin_data_dict = get_origin_data(freq, stock_codes)
        fin_change = conbin_change(origin_data_dict)
        break
    e = fund_cons["持仓占比"].sum()
    fin_change_weighted = fin_change
    fin_change_weighted_temp = fin_change * fund_cons.set_index("股票简称")["持仓占比"] / e
    fin_change_weighted["加权合计"] = fin_change_weighted_temp.apply(lambda x: x.sum(), axis=1)
    return fin_change_weighted.applymap(lambda x: '%.2f%%' % (x * 100))

# 多基金数据获取并打印
def mult_fund_display(fund_codes, freq):
    for i in fund_codes:
        # displaying the DataFrame
        print("基金编号:" + i)
        print(tabulate(get_fin_change_weighted(i, freq).tail(10), headers='keys', tablefmt='pretty'))


