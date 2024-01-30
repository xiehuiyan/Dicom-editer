#! /usr/bin/env python
# coding=utf-8
import os.path
import tkinter as tk
from lxml import etree
from tkinter import filedialog
from tkinter import ttk
import dicom_lib


class MyApp(tk.Tk):
    def __init__(self):
        self.datatype_list = ["CS", "SH", "LO", "ST", "LT", "UT", "AE", "PN", "UI", "DA", "TM", "DT", "AS", "IS", "DS",
                              "SS", "US", "SL", "UL", "AT", "FL", "FD", "OB", "OW", "OF", "SQ", "UN"]
        self.config = XMLobj()
        self.tagsel = self.config.tags
        self.maininfo = self.config.maindict
        self.log_printer = dicom_lib.init_logger(self)
        self.tag_numb = {}
        self.tag_value = {}
        self.tag_type = {}
        tk.Tk.__init__(self)
        # self.pack() # 若继承 tk.Frame ，此句必须有！
        # 程序界面
        # win = tk.Tk(self)
        self.tag_rows = 10
        # self.wm_attributes('-topmost', 1)
        self.title("DicomTagEditor - BACKUP FIRST before any tag operation!!!")
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 1110
        height = 525
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.setupUI()
        self.disable_buttons()
        self.set_maininfo()

    def set_maininfo(self):
        for i in range(len(self.maininfo)):
            self.tag_numb[i+1].set(self.maininfo[i]['tag'])
            self.tag_value[i + 1].set(self.maininfo[i]['value'])
            self.tag_type[i + 1].set(self.maininfo[i]['vr'])

    def write_config(self):
        self.config.maindict = []
        for i in range(1, self.tag_rows):
            tag = self.tag_numb[i].get()
            value = self.tag_value[i].get()
            vr = self.tag_type[i].get()
            if tag:
                self.config.maindict.append({'tag': tag, 'value': value, 'vr': vr})
                if tag not in self.tagsel:
                    self.config.tags.append(tag)
        self.config.xml_write()
        self.log_printer.info('保存配置文件成功')

    def setupUI(self):
        self.win_left()
        self.win_mid()
        self.win_right()

    def win_left(self):
        win_left = tk.Frame(self, bg='Gainsboro')
        win_left.pack(side=tk.LEFT, fill=tk.BOTH)
        win_left_top = tk.Frame(win_left, bg='Gainsboro')
        win_left_top.pack(side=tk.TOP, fill=tk.BOTH)

        open_frame = tk.Frame(win_left_top, bg='Gainsboro')
        open_frame.pack(side=tk.TOP, fill=tk.BOTH)
        self.open_type = tk.IntVar()
        self.open_type.set(2)
        tk.Radiobutton(open_frame, text="dicom文件", variable=self.open_type, value=1, bg='Gainsboro').pack(pady=5,
                                                                                                          padx=5,
                                                                                                          side=tk.LEFT)
        tk.Radiobutton(open_frame, text="文件夹", variable=self.open_type, value=2, bg='Gainsboro').pack(pady=5, padx=15,
                                                                                                      side=tk.LEFT)
        tk.Button(open_frame, text="打开", anchor=tk.CENTER, width=10, command=self.doopen).pack(
            pady=5, padx=5, side=tk.LEFT)
        self.folder_or_file = tk.StringVar()
        tk.Entry(win_left_top, fg="black", textvariable=self.folder_or_file, width=30, state='disabled').pack(pady=5, padx=5, side=tk.TOP,
                                                                                            fill=tk.X)

        win_left_mid = tk.Frame(win_left, bg='Gainsboro')
        win_left_mid.pack(side=tk.TOP, fill=tk.BOTH)

        tag_numb_col = tk.Frame(win_left_mid, bg='Gainsboro')
        tag_numb_col.pack(side=tk.LEFT, fill=tk.BOTH)
        tag_value_col = tk.Frame(win_left_mid, bg='Gainsboro')
        tag_value_col.pack(side=tk.LEFT, fill=tk.BOTH)
        tag_type_col = tk.Frame(win_left_mid, bg='Gainsboro')
        tag_type_col.pack(side=tk.LEFT, fill=tk.BOTH)
        tag_numb_combox = {}
        tag_type_combox = {}
        tk.Label(tag_numb_col, bg='Gainsboro', text="Tag(00100010)").pack(side=tk.TOP)
        tk.Label(tag_value_col, bg='Gainsboro', text="Value(Tom)").pack(side=tk.TOP)
        tk.Label(tag_type_col, bg='Gainsboro', text="VR(data type)").pack(side=tk.TOP)
        for i in range(1, self.tag_rows):
            self.tag_numb[i] = tk.StringVar()
            tag_numb_combox[i] = ttk.Combobox(tag_numb_col, width=11, textvariable=self.tag_numb[i])
            tag_numb_combox[i]["values"] = self.tagsel
            # tag_numb_combox[i].current(0)
            tag_numb_combox[i].pack(pady=1, padx=5, side=tk.TOP)
            self.tag_value[i] = tk.StringVar()
            tk.Entry(tag_value_col, fg="black", textvariable=self.tag_value[i], width=15).pack(pady=2, padx=5,
                                                                                               side=tk.TOP)

            self.tag_type[i] = tk.StringVar()
            tag_type_combox[i] = ttk.Combobox(tag_type_col, width=5, textvariable=self.tag_type[i])
            tag_type_combox[i]["values"] = self.datatype_list
            # tag_type_combox[i].current(0)
            tag_type_combox[i].pack(pady=1, padx=5, side=tk.TOP)

        self.win_left_bottom = tk.Frame(win_left, bg='Gainsboro')
        self.win_left_bottom.pack(side=tk.TOP, fill=tk.BOTH)

        button_col1 = tk.Frame(self.win_left_bottom, bg='Gainsboro')
        button_col1.pack(side=tk.LEFT, fill=tk.BOTH)
        button_col2 = tk.Frame(self.win_left_bottom, bg='Gainsboro')
        button_col2.pack(side=tk.LEFT, fill=tk.BOTH)
        button_col3 = tk.Frame(self.win_left_bottom, bg='Gainsboro')
        button_col3.pack(side=tk.LEFT, fill=tk.BOTH)
        button_width = 12
        button_pady = 5
        button_padx = 5
        tk.Button(button_col1, text="修改tag", anchor=tk.CENTER, width=button_width, command=self.doupdatetag).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col1, text="添加tag", anchor=tk.CENTER, width=button_width, command=self.doaddtag).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col1, text="删除tag", anchor=tk.CENTER, width=button_width, command=self.dodeletetag).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col1, text="生成新检查", anchor=tk.CENTER, width=button_width, command=self.donew_study).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col1, text="批量生成检查", anchor=tk.CENTER, width=button_width,
                  command=self.ask_new_copy_study_window).pack(pady=button_pady, padx=button_padx, side=tk.TOP)

        tk.Button(button_col2, text="匿名数据", anchor=tk.CENTER, width=button_width,
                  command=self.doanonymous_data).pack(pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col2, text="自定义匿名", anchor=tk.CENTER, width=button_width,
                  command=self.ask_custom_anonymous_window).pack(pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col2, text="添加子tag", anchor=tk.CENTER, width=button_width,
                  command=self.ask_add_child_tag_window).pack(pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col2, text="修改子tag", anchor=tk.CENTER, width=button_width,
                  command=self.ask_update_child_window).pack(pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col2, text="删除子tag", anchor=tk.CENTER, width=button_width,
                  command=self.ask_delete_child_tag_window).pack(pady=button_pady, padx=button_padx, side=tk.TOP)

        tk.Button(button_col3, text="重读tag", anchor=tk.CENTER, width=button_width, command=self.reload_tag_info).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col3, text="搜索tag", anchor=tk.CENTER, width=button_width, command=self.search_tag_info).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col3, text="清空log", anchor=tk.CENTER, width=button_width, command=self.clear_log).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col3, text="备份数据", anchor=tk.CENTER, width=button_width, command=self.docopy_data).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)
        tk.Button(button_col3, text="保存配置", anchor=tk.CENTER, width=button_width, command=self.write_config).pack(
            pady=button_pady, padx=button_padx, side=tk.TOP)

    def win_mid(self):
        win_mid = tk.Frame(self, bg='Gainsboro')
        win_mid.pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Label(win_mid, bg='Gainsboro', text="tag list").pack(pady=(10, 0), side=tk.TOP, fill=tk.X)
        self.tag_info_text = tk.Text(win_mid, width=80, height=50, bg="white", fg="black", state='disabled')
        self.tag_info_text.config(font=('宋体', 9))
        self.tag_info_text.pack(pady=10, padx=10, side=tk.TOP)

    def win_right(self):
        win_right = tk.Frame(self, bg='Gainsboro')
        win_right.pack(side=tk.LEFT, fill=tk.BOTH)
        tk.Label(win_right, bg='Gainsboro', text="log info").pack(pady=(10, 0), side=tk.TOP, fill=tk.X)
        self.log_control = tk.Text(win_right, width=40, height=150, bg="white", fg="black", state='disabled')
        # self.log_control.config(font=('宋体', 10))
        self.log_control.pack(pady=10, padx=10, side=tk.TOP)

    def disable_buttons(self):
        for frame in self.win_left_bottom.children.values():
            for button in frame.children.values():
                button['state'] = 'disabled'

    def enable_buttons(self):
        for frame in self.win_left_bottom.children.values():
            for button in frame.children.values():
                button['state'] = 'normal'

    def update_tag_info(self, tag_info):
        current_see = self.tag_info_text.index(tk.CURRENT)
        self.tag_info_text['state'] = 'normal'
        self.tag_info_text.delete(1.0, tk.END)
        self.tag_info_text.insert(1.0, tag_info)
        self.tag_info_text['state'] = 'disabled'
        self.tag_info_text.see(current_see)

    def clear_tag_info(self):
        self.tag_info_text['state'] = 'normal'
        self.tag_info_text.delete(1.0, tk.END)
        self.tag_info_text['state'] = 'disabled'

    def insert_log(self, line_info):
        self.log_control['state'] = 'normal'
        self.log_control.insert(tk.END, line_info + '\n')
        self.log_control['state'] = 'disabled'
        self.log_control.see('end')

    def clear_log(self):
        self.log_control['state'] = 'normal'
        self.log_control.delete(1.0, tk.END)
        self.log_control['state'] = 'disabled'

    def doopen(self):
        if self.open_type.get() == 1:
            self.open_path = filedialog.askopenfilename(filetypes=[('dicomfile', '.dcm'), ('allfile', '.*')],
                                                        title=u"选择dicom文件")
        else:
            self.open_path = filedialog.askdirectory(mustexist=True, title=u"选择检查文件夹")
        if self.open_path:
            self.folder_or_file.set(self.open_path)
            self.reload_tag_info()
            self.enable_buttons()

    def donew_study(self):
        dicom_lib.NewStudy(self.open_type.get(), self.open_path, {}).start()

    def reload_tag_info(self):
        if self.open_path:
            self.log_printer.info('载入tag信息')
            if self.open_type.get() == 1:
                tag_info = dicom_lib.readDicomFile_onefile(self.open_path)
                self.update_tag_info(tag_info)
            else:
                first_file = dicom_lib.get_first_file(self.open_path)
                if not first_file:
                    self.clear_tag_info()
                    self.log_printer.info('文件夹中没有dicom文件')
                else:
                    tag_info = dicom_lib.readDicomFile_onefile(first_file)
                    self.update_tag_info(tag_info)

    def search_tag_info(self):
        tag_list = []
        for i in range(1, self.tag_rows):
            tag = self.tag_numb[i].get()
            if tag:
                tag_list.append(int(tag, 16))
        if tag_list:
            self.log_printer.info('搜索tag信息')
            if self.open_type.get() == 1:
                tag_info = dicom_lib.search_tag_onefile(self.open_path, tag_list)
                self.log_printer.info(tag_info)
            else:
                first_file = dicom_lib.get_first_file(self.open_path)
                if not first_file:
                    self.clear_tag_info()
                    self.log_printer.info('文件夹中没有dicom文件')
                else:
                    tag_info = dicom_lib.search_tag_onefile(first_file, tag_list)
                    self.log_printer.info(tag_info)
        else:
            self.log_printer.info('未输入搜索tag')
        dicom_lib.logger_end()

    def doupdatetag(self):
        tag_dict = {}
        for i in range(1, self.tag_rows):
            tag = self.tag_numb[i].get()
            value = self.tag_value[i].get()
            if tag and value:
                tag_dict[int(tag, 16)] = value
        if tag_dict:
            dicom_lib.UpdateTag(self.open_type.get(), self.open_path, tag_dict).start()
        else:
            self.log_printer.info('tag 信息为空')

    def doupdatechildtag(self, tag_dict):
        dicom_lib.UpdateChildTag(self.open_type.get(), self.open_path, tag_dict).start()

    def doaddtag(self):
        tag_dict = {}
        for i in range(1, self.tag_rows):
            tag = self.tag_numb[i].get()
            value = self.tag_value[i].get()
            vr = self.tag_type[i].get()
            if tag and vr:
                tag_dict[int(tag, 16)] = {'value': value, 'vr': vr}
        if tag_dict:
            dicom_lib.AddTag(self.open_type.get(), self.open_path, tag_dict).start()
        else:
            self.log_printer.info('tag或vr信息为空')

    def doaddchildtag(self, tag_dict):
        dicom_lib.AddChildTag(self.open_type.get(), self.open_path, tag_dict).start()

    def dodeletechildtag(self, tag_dict):
        dicom_lib.DeleteChildTag(self.open_type.get(), self.open_path, tag_dict).start()

    def dodeletetag(self):
        tag_dict = []
        for i in range(1, self.tag_rows):
            tag = self.tag_numb[i].get()
            if tag:
                tag_dict.append(tag)
        if tag_dict:
            dicom_lib.DeleteTag(self.open_type.get(), self.open_path, tag_dict).start()
        else:
            self.log_printer.info('tag 信息为空')

    def doanonymous_data(self):
        dicom_lib.AnonymousData(self.open_type.get(), self.open_path, {}).start()

    def docustomanonymous(self, patient_name):
        dicom_lib.CustomAnonymous(self.open_type.get(), self.open_path, patient_name).start()

    def docopy_data(self):
        dicom_lib.CopyData(self.open_type.get(), self.open_path, {}).start()

    def ask_new_copy_study_window(self):
        inputDialog = MultiNewStudy(self)
        self.wait_window(inputDialog)

    def ask_update_child_window(self):
        inputDialog = UpdateChildTagwin(self)
        self.wait_window(inputDialog)

    def ask_custom_anonymous_window(self):
        inputDialog = CustomAnonymous(self)
        self.wait_window(inputDialog)

    def ask_add_child_tag_window(self):
        inputDialog = AddChildTagwin(self)
        self.wait_window(inputDialog)

    def ask_delete_child_tag_window(self):
        inputDialog = DeleteChildTagwin(self)
        self.wait_window(inputDialog)

    def donew_copy_study(self, study_count):
        dicom_lib.NewCopyStudy(self.open_type.get(), self.open_path, study_count).start()


# 弹窗1
class MultiNewStudy(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self)
        self.title('新增数据确认')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 300
        height = 130
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.focus_set()
        # 弹窗界面
        self.setup_UI()
        self.bind('<Escape>', self.cancel)
        self.bind('<Return>', self.ok)
        self.app = app

    def setup_UI(self):
        # 第一行（两列）
        win2 = tk.Frame(self)
        win2.pack(fill="x", pady=5)
        tk.Label(win2, text="输入新生成数量:").pack(pady=5)
        self.new_study_count = tk.StringVar()
        tk.Entry(win2, fg="black", textvariable=self.new_study_count, width=25, font=('Arial', '13')).pack(pady=5)
        self.new_study_count.set('10')

        # 第三行
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        buttoncal = tk.Button(row3, text="取消", width=10)
        buttoncal.pack(pady=0, padx=30, side=tk.RIGHT)
        buttoncal.bind('<Button-1>', self.cancel)
        buttonok = tk.Button(row3, text="确定", width=10)
        buttonok.pack(pady=0, padx=30, side=tk.LEFT)
        buttonok.bind('<Button-1>', self.ok)

    def ok(self, event):
        study_count = self.new_study_count.get()  # 设置数据
        self.destroy()  # 销毁窗口
        app.donew_copy_study(study_count)

    def cancel(self, event):
        self.destroy()


# 弹窗2
class CustomAnonymous(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self)
        self.title('匿名确认')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 300
        height = 130
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.focus_set()
        # 弹窗界面
        self.setup_UI()
        self.bind('<Escape>', self.cancel)
        self.bind('<Return>', self.ok)
        self.app = app

    def setup_UI(self):
        # 第一行（两列）
        win2 = tk.Frame(self)
        win2.pack(fill="x", pady=5)
        tk.Label(win2, text="输入匿名名称:").pack(pady=5)
        self.custom_patient_name = tk.StringVar()
        tk.Entry(win2, fg="black", textvariable=self.custom_patient_name, width=25, font=('Arial', '13')).pack(pady=5)
        self.custom_patient_name.set('Anonymous')

        # 第三行
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        buttoncal = tk.Button(row3, text="取消", width=10)
        buttoncal.pack(pady=0, padx=30, side=tk.RIGHT)
        buttoncal.bind('<Button-1>', self.cancel)
        buttonok = tk.Button(row3, text="确定", width=10)
        buttonok.pack(pady=0, padx=30, side=tk.LEFT)
        buttonok.bind('<Button-1>', self.ok)

    def ok(self, event):
        patient_name = self.custom_patient_name.get()  # 设置数据
        self.destroy()  # 销毁窗口
        app.docustomanonymous(patient_name)

    def cancel(self, event):
        self.destroy()


# 弹窗3
class AddChildTagwin(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self)
        self.title('添加子tag')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 300
        height = 230
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.focus_set()
        # 弹窗界面
        self.bind('<Escape>', self.cancel)
        self.bind('<Return>', self.ok)
        self.app = app
        self.parent_tag = tk.StringVar()
        self.parent_index = tk.StringVar()
        self.child_tag = tk.StringVar()
        self.child_value = tk.StringVar()
        self.child_VR = tk.StringVar()
        self.setup_UI()

    def setup_UI(self):
        # 第一行（两列）
        win2 = tk.Frame(self)
        win2.pack(fill="x", pady=5)
        win21 = tk.Frame(win2)
        win21.pack(padx=(15, 0), pady=5, side=tk.LEFT)
        win22 = tk.Frame(win2)
        win22.pack(padx=(0, 15), pady=5, side=tk.LEFT)
        tk.Label(win21, text="父tag(已存在的SQ):").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="父tag index:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag value:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag VR:").pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.parent_tag, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.parent_index, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_tag, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_value, width=20).pack(pady=5, side=tk.TOP)
        tag_type_combox = ttk.Combobox(win22, textvariable=self.child_VR, width=10)
        tag_type_combox["values"] = app.datatype_list
        tag_type_combox.pack(pady=5, side=tk.TOP)

        # 第三行
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        buttoncal = tk.Button(row3, text="取消", width=10)
        buttoncal.pack(pady=0, padx=30, side=tk.RIGHT)
        buttoncal.bind('<Button-1>', self.cancel)
        buttonok = tk.Button(row3, text="确定", width=10)
        buttonok.pack(pady=0, padx=30, side=tk.LEFT)
        buttonok.bind('<Button-1>', self.ok)

    def ok(self, event):
        tag_dict = {'parent_tag': int(self.parent_tag.get(), 16), 'parent_index': int(self.parent_index.get()),
                    'child_tag': int(self.child_tag.get(), 16), 'child_value': self.child_value.get(),
                    'child_VR': self.child_VR.get()}
        self.destroy()
        app.doaddchildtag(tag_dict)

    def cancel(self, event):
        self.destroy()


class UpdateChildTagwin(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self)
        self.title('修改子tag')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 300
        height = 160
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.focus_set()
        # 弹窗界面
        self.bind('<Escape>', self.cancel)
        self.bind('<Return>', self.ok)
        self.app = app
        self.child_index = tk.StringVar()
        self.child_tag = tk.StringVar()
        self.child_value = tk.StringVar()
        self.setup_UI()

    def setup_UI(self):
        # 第一行（两列）
        win2 = tk.Frame(self)
        win2.pack(fill="x", pady=5)
        win21 = tk.Frame(win2)
        win21.pack(padx=(15, 0), pady=5, side=tk.LEFT)
        win22 = tk.Frame(win2)
        win22.pack(padx=(0, 15), pady=5, side=tk.LEFT)
        tk.Label(win21, text="子tag:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag index:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag value:").pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_tag, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_index, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_value, width=20).pack(pady=5, side=tk.TOP)
        # self.custom_patient_name.set('Anonymous')

        # 第三行
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        buttoncal = tk.Button(row3, text="取消", width=10)
        buttoncal.pack(pady=0, padx=30, side=tk.RIGHT)
        buttoncal.bind('<Button-1>', self.cancel)
        buttonok = tk.Button(row3, text="确定", width=10)
        buttonok.pack(pady=0, padx=30, side=tk.LEFT)
        buttonok.bind('<Button-1>', self.ok)

    def ok(self, event):
        tag_dict = {'child_index': int(self.child_index.get()), 'child_tag': int(self.child_tag.get(), 16),
                    'child_value': self.child_value.get()}
        self.destroy()
        app.doupdatechildtag(tag_dict)

    def cancel(self, event):
        self.destroy()


class DeleteChildTagwin(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self)
        self.title('删除子tag')
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        width = 300
        height = 200
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)
        self.focus_set()
        # 弹窗界面
        self.bind('<Escape>', self.cancel)
        self.bind('<Return>', self.ok)
        self.app = app
        self.parent_index = tk.StringVar()
        self.parent_tag = tk.StringVar()
        self.child_index = tk.StringVar()
        self.child_tag = tk.StringVar()
        self.setup_UI()

    def setup_UI(self):
        # 第一行（两列）
        win2 = tk.Frame(self)
        win2.pack(fill="x", pady=5)
        win21 = tk.Frame(win2)
        win21.pack(padx=(15, 0), pady=5, side=tk.LEFT)
        win22 = tk.Frame(win2)
        win22.pack(padx=(0, 15), pady=5, side=tk.LEFT)
        tk.Label(win21, text="父tag:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="父tag index:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag:").pack(pady=5, side=tk.TOP)
        tk.Label(win21, text="子tag 内index:").pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.parent_tag, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.parent_index, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_tag, width=20).pack(pady=5, side=tk.TOP)
        tk.Entry(win22, fg="black", textvariable=self.child_index, width=20).pack(pady=5, side=tk.TOP)
        # self.custom_patient_name.set('Anonymous')

        # 第三行
        row3 = tk.Frame(self)
        row3.pack(fill="x", pady=5)
        buttoncal = tk.Button(row3, text="取消", width=10)
        buttoncal.pack(pady=0, padx=30, side=tk.RIGHT)
        buttoncal.bind('<Button-1>', self.cancel)
        buttonok = tk.Button(row3, text="确定", width=10)
        buttonok.pack(pady=0, padx=30, side=tk.LEFT)
        buttonok.bind('<Button-1>', self.ok)

    def ok(self, event):
        tag_dict = {'child_index': int(self.child_index.get()), 'child_tag': int(self.child_tag.get(), 16),
                    'parent_tag': int(self.parent_tag.get(), 16), 'parent_index': int(self.parent_index.get())}
        self.destroy()
        app.dodeletechildtag(tag_dict)

    def cancel(self, event):
        self.destroy()


class XMLobj:
    def __init__(self):
        self.maindict = []
        self.tags = ['00100010', '00100020']
        self.configfile = 'dicomconfig.xml'
        self.xml_read()

    def xml_read(self):
        if os.path.exists(self.configfile):
            self.tags = []
            tree = etree.parse(self.configfile)
            mainwin = tree.xpath('//mainwin')
            for elem in mainwin[0]:
                tag = elem[0].text
                value = elem[1].text if elem[1].text else ''
                vr = elem[2].text if elem[2].text else ''
                self.maindict.append({'tag': tag, 'value': value, 'vr': vr})
            tagsel = tree.xpath('//tagsel')
            for tage in tagsel[0]:
                self.tags.append(tage.text)

    def xml_write(self):
        root = etree.Element("root")
        mainwin = etree.Element("mainwin")
        for taginfo in self.maindict:
            elem = etree.Element('elem')
            tag = etree.Element('tag')
            tag.text = taginfo['tag']
            value = etree.Element('value')
            value.text = taginfo['value']
            vr = etree.Element('vr')
            vr.text = taginfo['vr']
            elem.append(tag)
            elem.append(value)
            elem.append(vr)
            mainwin.append(elem)
        root.append(mainwin)
        tagsel = etree.Element('tagsel')
        for tag in self.tags:
            etag = etree.Element('tag')
            etag.text = tag
            tagsel.append(etag)
        root.append(tagsel)
        tree = etree.ElementTree(root)
        tree.write(self.configfile, encoding="utf-8", xml_declaration=True, pretty_print=True)


if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
