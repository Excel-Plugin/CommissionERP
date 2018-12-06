# -*- coding: utf-8 -*-
from datetime import datetime
import CalcRatio
import  types
# 来自售后员提成明细表
# 注意：此处的地名一定要与数据源表中的地名完全一致
# TODO: 售后员表有两种类型，目前只考虑了第一种
default_psn2plc = {"戴梦菲": ["龙华", "观澜","纳诺-观澜"],
                   "李飞": ["济源","纳诺-济源"],
                   "卢伟": ["郑州港区", "郑州加工区", "鹤壁", "锜昌", "建泰"],
                   "周文斌": ["廊坊", "太原", "烟台"]}


class Bonus(object):

    def __init__(self, price,psn2plc=default_psn2plc):
        self.price=price
        self.plc2psn = {}
        for psn, plcs in psn2plc.items():
            for plc in plcs:
                self.plc2psn[plc] = psn
        # 表头各属性名称，按顺序放置
        self.header = [ "业务", "开票日期", "客户编号", "客户名称",
                       "开票金额（含税）", "发票号码", "到期时间", "款期", "付款日",
                       "付款金额（含税）", "付款未税金额", "到款天数", "未税服务费", "客户类型",
                       "提成比例", "提成金额", "我司单价", "公司指导价合计", "实际差价",
                       "成品代码", "品名", "规格", "数量", "单位",
                       "单价", "含税金额", "重量", "单桶公斤数量", "指导价",
                       "单号", "出货时间", "出货地点","税率"]
        self.rst_dict = {}
        for i, attr in enumerate(self.header):
            self.rst_dict[attr] = i

    def calc_commission(self, src_dict, src_data, clt_dict, client_dict,rule_dict,rule_data,place,leader):
        """根据数据源表计算各售后服务员提成"""
        # TODO: 写入Excel的时候记得把所有float型数据按照保留两位小数显示
        # TODO: 添加汇总行
        ruleUtil=CalcRatio.CalcRatio(rule_dict,rule_data)
        result = []  # 结果表数据
        print(len(src_data))
        for rcd in src_data:

            row = ["" for _ in range(0, len(self.rst_dict))]  # 注意这里不能用[]*len(self.rst_dict)（复制的是引用）

            row[self.rst_dict['业务']] = rcd[src_dict['业务']]
            row[self.rst_dict['开票日期']] = rcd[src_dict['开票日期']].split(" ")[0]
            row[self.rst_dict['客户编号']] = rcd[src_dict['客户编号']]
            row[self.rst_dict['客户名称']] = rcd[src_dict['客户名称']]
            row[self.rst_dict['开票金额（含税）']] = rcd[src_dict['金额']]
            row[self.rst_dict['发票号码']] = rcd[src_dict['发票号码']]
            if row[self.rst_dict['发票号码']]!="未税":
                row[self.rst_dict['发票号码']]="'"+row[self.rst_dict['发票号码']]

            row[self.rst_dict['到期时间']] = rcd[src_dict['到期时间']].split(" ")[0]
            row[self.rst_dict['款期']] = rcd[src_dict['款期']]
            row[self.rst_dict['付款日']] = rcd[src_dict['付款日']].split(" ")[0]
            row[self.rst_dict['付款金额（含税）']] = rcd[src_dict['付款金额']]
            # 注意此处可能因为编码不同导致相等关系不成立
            if rcd[src_dict['发票号码']] == "未税"  or (not self.is_number(rcd[src_dict['税率']])):
                row[self.rst_dict['付款未税金额']] = float(rcd[src_dict['付款金额']])

            else:
                row[self.rst_dict['付款未税金额']] = float(rcd[src_dict['付款金额']]) / (1+float(rcd[src_dict['税率']]))
            # 值格式为'2018-04-23 00:00:00+00:00'，所以要split(' ')[0]
            # 这里的付款日格式可能形如'2018-3-31/2018-4-4'，计算时只使用最后的日期，所以要split('/')[-1]
            row[self.rst_dict['到款天数']] = \
                (datetime.strptime(rcd[src_dict['付款日']].split(' ')[0].split('/')[-1], "%Y-%m-%d")
                 - datetime.strptime(rcd[src_dict['开票日期']].split(' ')[0], "%Y-%m-%d")).days


            row[self.rst_dict['未税服务费']] = 0    # Todo:不需要计算
            if rcd[src_dict['未税服务费']] !="None":
                row[self.rst_dict['未税服务费']]=rcd[src_dict['未税服务费']]


            row[self.rst_dict['提成比例']] = 0
            row[self.rst_dict['客户类型']] = client_dict[rcd[src_dict['客户编号']]][clt_dict['提成计算方式']]

            row[self.rst_dict['提成金额']] = float(rcd[src_dict['数量（桶）']])*row[self.rst_dict['提成比例']]
            row[self.rst_dict['我司单价']] = ""  # 不需要计算
            row[self.rst_dict['公司指导价合计']] = ""  # 不需要计算
            row[self.rst_dict['实际差价']] = ""  # 不需要计算
            row[self.rst_dict['成品代码']] = rcd[src_dict['成品代码']]
            row[self.rst_dict['品名']] = rcd[src_dict['品名']]
            row[self.rst_dict['规格']] = rcd[src_dict['规格']]
            row[self.rst_dict['数量']] = rcd[src_dict['数量（桶）']]
            row[self.rst_dict['单位']] = rcd[src_dict['单位']]
            row[self.rst_dict['单价']] = rcd[src_dict['单价']]
            row[self.rst_dict['含税金额']] = rcd[src_dict['含税金额']]
            row[self.rst_dict['数量']] = rcd[src_dict['数量（桶）']]
            row[self.rst_dict['重量']] = rcd[src_dict['重量（公斤）']]
            row[self.rst_dict['单桶公斤数量']] = rcd[src_dict['单桶重量']]
            row[self.rst_dict['指导价']] = "指导价"
            if float(row[self.rst_dict['单桶公斤数量']])<50:
                row[self.rst_dict['指导价']] = "指导价+Y4*30"
            row[self.rst_dict['单号']] = rcd[src_dict['单号']]
            row[self.rst_dict['出货时间']] = rcd[src_dict['出货时间']].split(" ")[0]
            row[self.rst_dict['出货地点']] = rcd[src_dict['出货地点']]
            row[self.rst_dict['税率']] = rcd[src_dict['税率']]
            tmp1,tmp2=ruleUtil.calc(row[self.rst_dict['出货时间']],row[self.rst_dict['客户类型']],row[self.rst_dict['到款天数']],row[self.rst_dict['品名']])

            price_arr=self.check_price(row[self.rst_dict['成品代码']],row[self.rst_dict['出货时间']])

            tcp=0.0
            if row[self.rst_dict['客户类型']] == "正常计算":
                tcp=float(row[self.rst_dict['付款未税金额']])-float(row[self.rst_dict['未税服务费']])
            else:
                tcp=float(row[self.rst_dict['付款未税金额']])

            if(price_arr != None):
                pr0=price_arr[0]
                pr1=price_arr[1]
                row[self.rst_dict['我司单价']]=float(pr0)
                row[self.rst_dict['我司单价']] = round(row[self.rst_dict['我司单价']], 4)
                if('出货算差价不加价' in pr1):
                    row[self.rst_dict['指导价']]="指导价"
                    print("触发特殊情况：出货算差价不加价")
                if row[self.rst_dict['客户类型']]=="正常计算"  and  row[self.rst_dict['到款天数']]<=180:
                    if  row[self.rst_dict['指导价']]=="指导价":
                        row[self.rst_dict['公司指导价合计']]=float(row[self.rst_dict['重量']])*float(row[self.rst_dict['我司单价']])
                    else:
                        row[self.rst_dict['公司指导价合计']] = float(row[self.rst_dict['重量']]) * float(row[self.rst_dict['我司单价']])+float(row[self.rst_dict['数量']])*30
                    row[self.rst_dict['实际差价']]= tcp- row[self.rst_dict['公司指导价合计']]
                    row[self.rst_dict['实际差价']] = round(row[self.rst_dict['实际差价']], 2)
                    row[self.rst_dict['公司指导价合计']] = round(row[self.rst_dict['公司指导价合计']], 2)


            row[self.rst_dict['付款未税金额']] = round(row[self.rst_dict['付款未税金额']], 2)



            if type(tmp1) == type(1.0):
                row[self.rst_dict['提成比例']] = tmp1
                if (tmp1 >= 1.0):
                    if self.in_place(row[self.rst_dict['出货地点']],place,row[self.rst_dict['出货时间']]) :
                        row[self.rst_dict['提成金额']] = float(rcd[src_dict['数量（桶）']]) * tmp1 * (1 - tmp2)
                        row[self.rst_dict['提成比例']]=tmp1 * (1 - tmp2)
                    else:
                        row[self.rst_dict['提成金额']] = float(rcd[src_dict['数量（桶）']]) * tmp1
                else:
                    if self.in_place(row[self.rst_dict['出货地点']], place, row[self.rst_dict['出货时间']]):
                        row[self.rst_dict['提成金额']] = tcp * (1 - tmp2) * tmp1
                        row[self.rst_dict['提成比例']] = tmp1 * (1 - tmp2)
                        print("提成比例为：")
                        print(row[self.rst_dict['提成比例']])
                    else:

                        row[self.rst_dict['提成金额']] = tcp  * tmp1
                row[self.rst_dict['提成金额']] = round(row[self.rst_dict['提成金额']], 2)
                result.append(row)
            else:
                for cnt in range(len(tmp1)):

                    row[self.rst_dict['提成比例']]=tmp2[cnt]
                    row[self.rst_dict['提成金额']] = tcp  * float(tmp2[cnt])
                    row[self.rst_dict['提成金额']] = round(row[self.rst_dict['提成金额']], 2)
                    row[self.rst_dict['业务']] = tmp1[cnt]
                    row1=row.copy()
                    result.append(row1)

            for i in leader:
                if row[self.rst_dict['业务']]==i[0] and row[self.rst_dict['出货时间']]>=i[2] and row[self.rst_dict['出货时间']]<=i[3] and row[self.rst_dict['客户类型']]==i[4]:
                    row1=row.copy()
                    row1[self.rst_dict['业务']]=i[1]
                    row1[self.rst_dict['提成比例']] = tmp1 * float(i[5])
                    row1[self.rst_dict['提成金额']]=float(rcd[src_dict['数量（桶）']]) * row1[self.rst_dict['提成比例']]
                    row[self.rst_dict['提成金额']] = round(row[self.rst_dict['提成金额']], 2)
                    result.append(row1)








        result.sort(key=lambda row: row[self.rst_dict['业务']])

        result2 = []
        name=result[0][0]
        adder1=0.0
        adder2 = 0.0
        adder3 = 0.0
        adder4 = 0.0
        adder5 = 0.0
        adder6 = 0.0

        for i in result:
            if(i[0]!=name):
                row = ["" for _ in range(0, len(self.rst_dict))]
                row[self.rst_dict['业务']]=name
                row[self.rst_dict['开票日期']]="汇总"
                row[self.rst_dict['开票金额（含税）']]=round(adder1,2)
                row[self.rst_dict['付款金额（含税）']] = round(adder2,2)
                row[self.rst_dict['付款未税金额']] = round(adder3,2)
                row[self.rst_dict['提成金额']] = round(adder4,2)
                row[self.rst_dict['公司指导价合计']] = round(adder5,2)
                row[self.rst_dict['实际差价']] = round(adder6,2)
                name=i[0]
                adder1=0.0
                adder2 = 0.0
                adder3 = 0.0
                adder4 = 0.0
                adder5 = 0.0
                adder6 = 0.0
                result2.append(row)
            result2.append(i)
            adder1=adder1+float(i[self.rst_dict['开票金额（含税）']])
            adder2=adder2+float(i[self.rst_dict['付款金额（含税）']])
            adder3 = adder3 + float(i[self.rst_dict['付款未税金额']])
            adder4 = adder4 + float(i[self.rst_dict['提成金额']])
            if self.is_number(i[self.rst_dict['公司指导价合计']]):
                adder5 = adder5 + float(i[self.rst_dict['公司指导价合计']])
            if self.is_number(i[self.rst_dict['实际差价']]):
                adder6 = adder6 + float(i[self.rst_dict['实际差价']])
        row = ["" for _ in range(0, len(self.rst_dict))]
        row[self.rst_dict['业务']] = name
        row[self.rst_dict['开票日期']] = "汇总"
        row[self.rst_dict['开票金额（含税）']] = round(adder1, 2)
        row[self.rst_dict['付款金额（含税）']] = round(adder2, 2)
        row[self.rst_dict['付款未税金额']] = round(adder3, 2)
        row[self.rst_dict['提成金额']] = round(adder4, 2)
        row[self.rst_dict['公司指导价合计']] = round(adder5, 2)
        row[self.rst_dict['实际差价']] = round(adder6, 2)
        result2.append(row)




        return self.header, result,result2  # TODO: 由于不知道接口是否支持直接写入int,float，所以暂且没有将非str类型进行转换

    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    def in_place(self,x,place,t):
        res=False
        for i in place:
            if (i[0] in x) and (i[1]<=t) and (t<=i[2]) :
                return True
        return res

    def check_price(self,x,t):
        for i in self.price:
            if (x==i[0]) and (i[3]<=t) and (t<=i[4]):
                return [i[1],i[2]]
        print("no such product: "+ x)
        return None
