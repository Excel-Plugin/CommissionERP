# -*- coding: utf-8 -*-
# TODO：各种类型的表都应该有一个类
import logging


class ExcelCheck(object):

    # 注意：要导入的Excel表必须遵循以下格式
    # 要导入的列的列名必须包括以下关键字（所有符号均应该使用中文符号，不能使用英文符号）
    headers = {"数据源表": [],
               "售后员表": [],
               "客户编号表": [],
               "规则表": [],
               "指导价表": [],
               "主管表": [],
               "业务员提成明细": ["业务", "开票日期", "客户编号", "客户名称",
                           "开票金额（含税）", "发票号码", "到期时间", "款期", "付款日",
                           "付款金额（含税）", "付款未税金额", "到款天数", "未税服务费", "客户类型",
                           "提成比例", "提成金额", "我司单价", "公司指导价合计", "实际差价",
                           "成品代码", "品名", "规格", "数量", "单位",
                           "单价", "含税金额", "重量", "单桶公斤数量", "指导价",
                           "单号", "出货时间", "出货地点", "税率"],
               "售后员提成明细": ["售后", "业务", "开票日期", "客户编号", "客户名称",
                           "开票金额（含税）", "发票号码", "到期时间", "款期", "付款日",
                           "付款金额（含税）", "付款未税金额", "到款天数", "未税服务费", "客户类型",
                           "提成比例", "提成金额", "我司单价", "公司指导价合计", "实际差价",
                           "成品代码", "品名", "规格", "数量", "单位",
                           "单价", "含税金额", "重量", "单桶公斤数量", "指导价",
                           "单号", "出货时间", "出货地点"]
               }

    @staticmethod
    def formatted_after_sales(org_dict: dict, org_data: list):
        return ExcelCheck.__formatted(ExcelCheck.headers["售后员提成明细"], org_dict, org_data)

    @staticmethod
    def __formatted(header: list, org_dict: dict, org_data: list):
        """输入原先的表头字典org_dict和sheet数据org_data（二维数组），输出按照header格式整理的sheet数据
        org_dict中包含了本类中定义的header的表头对应的列数据将会被留下来，不包含的将不会保留。如“A售后”会被保留，但是“学校”将不会"""
        tmp_dict = {name: i for i, name in enumerate(header)}
        sheet_data = [["" for j in range(len(tmp_dict))] for i in range(len(org_data))]
        for org_name, org_index in org_dict.items():
            for name, index in tmp_dict.items():
                if name in org_name:  # header_dict的名称在本列名中出现了，则将其填写至相应位置
                    # print(f"{name} in {repr(org_name)}")  # 使用repr可以直接输出转义字符本身，如不换行而直接输出\n，且会打印两边的''
                    for i in range(len(org_data)):
                        sheet_data[i][index] = org_data[i][org_index]
                        # print(f"sheet_data[{i}][{name}]=org_data[{i}][{repr(org_name)}]"
                        #       f"={repr(org_data[i][org_index])}")
                    tmp_dict.pop(name)
                    break
        if len(tmp_dict) > 0:
            logging.warning(f"有{str(len(tmp_dict))}列没有填：" + str(tmp_dict))
        return sheet_data
