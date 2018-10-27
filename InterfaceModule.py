# -*- coding: utf-8 -*-
import win32com.client
import os
import pickle
import win32timezone  # 程序打包需要用到这个包，否则会报错


# def cache(get_sheet):
#     """Easyexcel类中get_sheet函数的装饰器，用于自动缓存被使用过的sheet
#     注意：若sheet被修改了，将cached_sheets下对应的pickle文件删除即可，之后调用get_sheet时会自动生成"""
#
#     def inner(self, sheet_name):
#
#         if os.path.exists("cached_sheets/" + self.filename + "/" + sheet_name + ".pickle"):
#             print("exists " + sheet_name)
#             with open("cached_sheets/" + self.filename + "/" + sheet_name + ".pickle", "rb") as f:
#                 return pickle.load(f)
#         else:
#             print("gen " + sheet_name)
#             header_dict, sheet_data = get_sheet(self, sheet_name)
#             with open("cached_sheets/" + self.filename + "/" + sheet_name + ".pickle", "wb") as f:
#                 pickle.dump((header_dict, sheet_data), f)
#             return header_dict, sheet_data
#
#     return inner


class Easyexcel:
    def __init__(self, filepath, visible=True, access_password=None, write_res_password=None):
        if not os.path.isfile(filepath):  # 文件名不存在则新建文件
            app = win32com.client.Dispatch('Excel.Application')
            app.Workbooks.Add().SaveAs(filepath)
        self.xlApp = win32com.client.Dispatch('Excel.Application')
        self.xlApp.Visible = visible
        self.filepath = filepath  # 文件完整路径
        self.xlBook = self.xlApp.Workbooks.Open(Filename=filepath, UpdateLinks=2, ReadOnly=False, Format=None,
                                                Password=access_password, WriteResPassword=write_res_password)
        self.filename = os.path.basename(filepath)  # 文件名
        # if not os.path.isdir('cached_sheets/'):
        #     os.mkdir('cached_sheets/')
        # if not os.path.isdir('cached_sheets/' + self.filename):
        #     os.mkdir('cached_sheets/' + self.filename)

    def get_a_row(self, sheet_name, r, col_num=-1):
        """col_num<0,根据末尾连续空格数决定此行是否终止(用于读取表头);col_num>=0,读入长度为col_num的一行(用于读取普通数据)
        注意：在指定col_num情况下，该行只要有一个值不是None就会被返回整行，只有全为None时才会返回[]"""
        row = []
        if col_num < 0:
            c = 1  # col，本行要读入的列号，从1开始计数
            while str(self.xlBook.Worksheets(sheet_name).Cells(r, c)) != 'None' \
                    or str(self.xlBook.Worksheets(sheet_name).Cells(r, c + 1)) != 'None' \
                    or str(self.xlBook.Worksheets(sheet_name).Cells(r, c + 2)) != 'None':
                row.append(str(self.xlBook.Worksheets(sheet_name).Cells(r, c)))
                c += 1
        else:
            for c in range(1, col_num + 1):
                row.append(str(self.xlBook.Worksheets(sheet_name).Cells(r, c)))
            if row.count('None') >= col_num:  # 若该行全为None，则返回空行；反之只要有一个非None的值就正常返回row
                row = []
        return row

    # @cache
    def get_sheet(self, sheet_name):
        """读取Excel表中的一个sheet，返回表头各属性对应索引dict和数据表
        注意1：这里默认所有sheet都是矩阵，即所有行长度都等于表头长度
        注意2：这里默认sheet文件结尾前没有空行"""

        # 读取表头，属性-索引字典保存在header_dict中
        r = 1
        while len(self.get_a_row(sheet_name, r)) <= 0:
            r += 1
        header = self.get_a_row(sheet_name, r)  # 表头
        r += 1
        header_dict = {}
        for i, name in enumerate(header):
            if name not in header_dict:  # 表头重复者以第一个出现的为准
                header_dict[name] = i

        # 读取表中数据到data中
        sheet_data = []
        len_ = len(header)  # 表头长度（不能用header_dict，因为有的表头项会重复）
        row = self.get_a_row(sheet_name, r, len_)
        while row:
            sheet_data.append(row)
            r += 1
            row = self.get_a_row(sheet_name, r, len_)

        return header_dict, sheet_data

    def close(self):
        self.xlBook.Close(self.filepath)
        del self.xlApp

    def save(self):
        self.xlBook.Save()

    def set_sheet(self, sheet_name, header, content):
        """Excel支持写入int,float,str三种基本类型，其他类型不能保证
        注意：datetime类型绝对不能直接写入！必须以str类型写入！（否则写入结果是错误的）"""
        sht = self.xlBook.Worksheets(sheet_name)
        # 在第1行写入表头
        for j, attr in enumerate(header):
            sht.Cells(1, j+1).Value = attr
        # 从第2行开始写入数据
        for i, row in enumerate(content):
            for j, value in enumerate(row):
                if value != 'None':  # 若为空，则直接填空字符串
                    sht.Cells(i+2, j+1).Value = value
                else:
                    sht.Cells(i+2, j+1).Value = ""
        self.save()

    def create_sheet(self, sheet_name):
        sht = self.xlBook.Worksheets
        sht.Add(After='Sheet1').Name = sheet_name


if __name__ == '__main__':
    excel = Easyexcel(os.getcwd() + r"\test.xlsx")
    header_dict, sheet_data = excel.get_sheet("客户编号test")
    print(len(header_dict))
    print(len(sheet_data))
    print(header_dict)
    print("!!!!!")
    print(sheet_data)
