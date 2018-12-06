# -*- coding: utf-8 -*-
from datetime import datetime
from CalcRatio import CalcRatio


class Saler(object):
    """用于记录售后员的相关信息，相关数据都以其对应的数据类型存储，不应直接输入到Excel中"""

    def __init__(self, name):
        self.name = name
        self.places = {}  # 出货地点的集合
        self.clients = {}  # 客户的集合

    def add_a_row(self, slr_dict, slr_row):
        """注意：单条记录中出货地点与客户编号应有且只有一个存在值"""
        if (slr_row[slr_dict['出货地点']] != 'None' and slr_row[slr_dict['客户编号']] != 'None') \
                or (slr_row[slr_dict['出货地点']] != 'None' and slr_row[slr_dict['客户编号']] != 'None'):
            raise Exception("售后员表中单行'出货地点'与'客户编号'只能有且仅有一个存在值！")
        row = slr_row
        # 值格式为'2018-04-23 00:00:00+00:00'，所以要split(' ')[0]
        row[slr_dict['出货开始时间']] = \
            datetime.strptime(slr_row[slr_dict['出货开始时间']].split(' ')[0], '%Y-%m-%d')
        row[slr_dict['出货结束时间']] = \
            datetime.strptime(slr_row[slr_dict['出货结束时间']].split(' ')[0], '%Y-%m-%d')
        row[slr_dict['收款开始时间']] = \
            datetime.strptime(slr_row[slr_dict['收款开始时间']].split(' ')[0], '%Y-%m-%d')
        row[slr_dict['收款结束时间']] = \
            datetime.strptime(slr_row[slr_dict['收款结束时间']].split(' ')[0], '%Y-%m-%d')
        if slr_row[slr_dict['出货地点']] != 'None':
            self.places[slr_row[slr_dict['出货地点']]] = row
        if slr_row[slr_dict['客户编号']] != 'None':
            row[slr_dict['提成比例']] = float(row[slr_dict['提成比例']])
            self.clients[slr_row[slr_dict['客户编号']]] = row


class AfterSales(object):
    def __init__(self, slr_dict, slr_data):
        self.salers = {}
        self.slr_dict = slr_dict
        for row in slr_data:
            if row[slr_dict['售后员']] not in self.salers:
                saler = Saler(row[slr_dict['售后员']])
                saler.add_a_row(slr_dict, row)
                self.salers[row[slr_dict['售后员']]] = saler
            else:
                self.salers[row[slr_dict['售后员']]].add_a_row(slr_dict, row)
        # 表头各属性名称，按顺序放置
        self.header = ["售后", "业务", "开票日期", "客户编号", "客户名称",
                       "开票金额（含税）", "发票号码", "到期时间", "款期", "付款日",
                       "付款金额（含税）", "付款未税金额", "到款天数", "未税服务费", "客户类型",
                       "提成比例", "提成金额", "我司单价", "公司指导价合计", "实际差价",
                       "成品代码", "品名", "规格", "数量", "单位",
                       "单价", "含税金额", "重量", "单桶公斤数量", "指导价",
                       "单号", "出货时间", "出货地点"]
        self.rst_dict = {}
        for i, attr in enumerate(self.header):
            self.rst_dict[attr] = i
        print("AfterSales gened")

    def calc_commission(self, src_dict, src_data, clt_dict, client_dict, calc_ratio):
        """根据数据源表计算各售后服务员提成"""
        result = []  # 结果表数据
        for rcd_num, rcd in enumerate(src_data):
            # print(str(rcd_num) + '/' + str(len(src_data)-1))
            flag = False  # True为匹配到了地点，否则没有。用于确定提成计算方式
            place = rcd[src_dict['出货地点']]  # 该行记录对应的出货地点
            number = rcd[src_dict['客户编号']]  # 该行记录对应的客户编号
            shipment = datetime.strptime(rcd[src_dict['出货时间']].split(' ')[0], "%Y-%m-%d")  # 出货时间
            # 这里的付款日格式可能形如'2018-3-31/2018-4-4'，计算时只使用最后的日期，所以要split('/')[-1]
            payment = datetime.strptime(rcd[src_dict['付款日']].split(' ')[0].split('/')[-1], "%Y-%m-%d")  # 付款时间
            slrs = []  # 该行记录对应的售后，可能不只一个人
            for slr in self.salers.values():  # 匹配出货地点
                for plc in slr.places:  # 该售货员的地名出现在数据源表出货地点中
                    if plc in place \
                            and slr.places[plc][self.slr_dict['出货开始时间']] <= shipment <= slr.places[plc][
                                self.slr_dict['出货结束时间']] \
                            and slr.places[plc][self.slr_dict['收款开始时间']] <= payment <= slr.places[plc][
                                self.slr_dict['收款结束时间']]:
                        slrs.append(slr)
                        flag = True
            if len(slrs) <= 0:  # 出货地点匹配失败，匹配客户编号
                for slr in self.salers.values():
                    if number in slr.clients \
                            and slr.clients[number][self.slr_dict['出货开始时间']] <= shipment <= slr.clients[number][
                                self.slr_dict['出货结束时间']] \
                            and slr.clients[number][self.slr_dict['收款开始时间']] <= payment <= slr.clients[number][
                                self.slr_dict['收款结束时间']]:
                        slrs.append(slr)
            if len(slrs) <= 0:  # 没有对应的售后
                continue
            for slr in slrs:
                row = ["" for _ in range(0, len(self.rst_dict))]  # 注意这里不能用[]*len(self.rst_dict)（复制的是引用）
                row[self.rst_dict['售后']] = slr.name
                row[self.rst_dict['业务']] = rcd[src_dict['业务']]
                row[self.rst_dict['开票日期']] = rcd[src_dict['开票日期']].split(' ')[0]
                row[self.rst_dict['客户编号']] = rcd[src_dict['客户编号']]
                row[self.rst_dict['客户名称']] = rcd[src_dict['客户名称']]
                row[self.rst_dict['开票金额（含税）']] = round(float(rcd[src_dict['金额']]), 2)  # 保留两位小数
                # 首字符为单引号以标明此单元格为文本而非数字，避免发票号码首位的0丢失
                if row[self.rst_dict['发票号码']] != "未税":
                    row[self.rst_dict['发票号码']] = "'" + rcd[src_dict['发票号码']]
                row[self.rst_dict['到期时间']] = rcd[src_dict['到期时间']].split(' ')[0]
                row[self.rst_dict['款期']] = rcd[src_dict['款期']]
                row[self.rst_dict['付款日']] = rcd[src_dict['付款日']].split(' ')[0]
                row[self.rst_dict['付款金额（含税）']] = round(float(rcd[src_dict['付款金额']]), 2)
                if rcd[src_dict['发票号码']] == "未税":
                    row[self.rst_dict['付款未税金额']] = round(float(rcd[src_dict['付款金额']]), 2)
                else:
                    row[self.rst_dict['付款未税金额']] = round(
                        float(rcd[src_dict['付款金额']]) / (1 + float(rcd[src_dict['税率']])), 2)
                # 值格式为'2018-04-23 00:00:00+00:00'，所以要split(' ')[0]
                # 这里的付款日格式可能形如'2018-3-31/2018-4-4'，计算时只使用最后的日期，所以要split('/')[-1]
                row[self.rst_dict['到款天数']] = \
                    (payment - datetime.strptime(rcd[src_dict['开票日期']].split(' ')[0], "%Y-%m-%d")).days
                row[self.rst_dict['未税服务费']] = ""  # 不需要计算
                if flag:  # 匹配到地点，使用外部计算方法
                    r1, r2 = calc_ratio.calc(shipment, client_dict[number][clt_dict['提成计算方式']],
                                             row[self.rst_dict['到款天数']], rcd[src_dict['品名']],
                                             slr.name, rcd[src_dict['业务']])  # 第二项是售后员提成
                    row[self.rst_dict['提成比例']] = r1 * r2
                    row[self.rst_dict['提成金额']] = round(float(rcd[src_dict['数量（桶）']]) * r1 * r2, 2)
                else:  # 匹配到客户，按照售后表的提成比例
                    row[self.rst_dict['提成比例']] = float(slr.clients[number][self.slr_dict['提成比例']])
                    row[self.rst_dict['提成金额']] = \
                        round(row[self.rst_dict['提成比例']] * float(row[self.rst_dict['付款未税金额']]), 2)
                row[self.rst_dict['客户类型']] = client_dict[rcd[src_dict['客户编号']]][clt_dict['客户类型']]
                row[self.rst_dict['我司单价']] = ""  # 不需要计算
                row[self.rst_dict['公司指导价合计']] = ""  # 不需要计算
                row[self.rst_dict['实际差价']] = ""  # 不需要计算
                row[self.rst_dict['成品代码']] = rcd[src_dict['成品代码']]
                row[self.rst_dict['品名']] = rcd[src_dict['品名']]
                row[self.rst_dict['规格']] = rcd[src_dict['规格']]
                row[self.rst_dict['数量']] = float(rcd[src_dict['数量（桶）']])  # 不是钱的单位，不保留两位小数
                row[self.rst_dict['单位']] = rcd[src_dict['单位']]
                row[self.rst_dict['单价']] = rcd[src_dict['单价']]
                row[self.rst_dict['含税金额']] = rcd[src_dict['含税金额']]
                row[self.rst_dict['重量']] = rcd[src_dict['重量（公斤）']]
                row[self.rst_dict['单桶公斤数量']] = rcd[src_dict['单桶重量']]
                row[self.rst_dict['指导价']] = "指导价"  # 不需要计算
                row[self.rst_dict['单号']] = rcd[src_dict['单号']]
                row[self.rst_dict['出货时间']] = rcd[src_dict['出货时间']].split(' ')[0]
                row[self.rst_dict['出货地点']] = rcd[src_dict['出货地点']]
                result.append(row)
        print("result gened")

        # 计算售后员汇总
        result.sort(key=lambda row: row[self.rst_dict['售后']])  # 按照售后员人名进行排序
        print("排序完成")
        total = ["" for _ in range(0, len(self.rst_dict))]  # 所有售货员总计
        total[self.rst_dict['售后']] = "总计"
        total[self.rst_dict['开票金额（含税）']] = 0
        total[self.rst_dict['付款金额（含税）']] = 0
        total[self.rst_dict['付款未税金额']] = 0
        total[self.rst_dict['提成金额']] = 0
        tmp = ["" for _ in range(0, len(self.rst_dict))]  # 当前售后员累计
        tmp[self.rst_dict['售后']] = result[0][self.rst_dict['售后']]
        tmp[self.rst_dict['开票金额（含税）']] = 0
        tmp[self.rst_dict['付款金额（含税）']] = 0
        tmp[self.rst_dict['付款未税金额']] = 0
        tmp[self.rst_dict['提成金额']] = 0
        tmp[self.rst_dict['数量']] = 0
        i = 0
        while i < len(result):
            row = result[i]  # row不会遍历到售后员汇总行上
            # print(str(i)+'/'+str(len(result)))
            if tmp[self.rst_dict['售后']] != row[self.rst_dict['售后']]:
                tmp[self.rst_dict['售后']] += " 汇总"
                result.insert(i, tmp)
                i += 1
                tmp = ["" for _ in range(0, len(self.rst_dict))]  # 重置tmp，不能重用原先的（insert进去的是tmp的引用）
                tmp[self.rst_dict['售后']] = row[self.rst_dict['售后']]
                tmp[self.rst_dict['开票金额（含税）']] = 0
                tmp[self.rst_dict['付款金额（含税）']] = 0
                tmp[self.rst_dict['付款未税金额']] = 0
                tmp[self.rst_dict['提成金额']] = 0
                tmp[self.rst_dict['数量']] = 0
            tmp[self.rst_dict['开票金额（含税）']] += row[self.rst_dict['开票金额（含税）']]
            tmp[self.rst_dict['付款金额（含税）']] += row[self.rst_dict['付款金额（含税）']]
            tmp[self.rst_dict['付款未税金额']] += row[self.rst_dict['付款未税金额']]
            tmp[self.rst_dict['提成金额']] += row[self.rst_dict['提成金额']]
            tmp[self.rst_dict['数量']] += row[self.rst_dict['数量']]
            total[self.rst_dict['开票金额（含税）']] += row[self.rst_dict['开票金额（含税）']]
            total[self.rst_dict['付款金额（含税）']] += row[self.rst_dict['付款金额（含税）']]
            total[self.rst_dict['付款未税金额']] += row[self.rst_dict['付款未税金额']]
            total[self.rst_dict['提成金额']] += row[self.rst_dict['提成金额']]
            i += 1
        tmp[self.rst_dict['售后']] += " 汇总"
        result.append(tmp)
        result.append(total)
        print("汇总完成")
        return self.header, result
