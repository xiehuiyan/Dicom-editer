# coding=utf-8

import os
import stat
import traceback
from pydicom import dicomio, sequence, DataElement, Dataset
import copy
import threading
import time
import uuid
import shutil


class LoggerPrinter:
    def __init__(self, app):
        self.app = app

    def info(self, info):
        self.app.insert_log(str(info))

    def error(self, info):
        self.app.insert_log(str(info))

    def warning(self, info):
        self.app.insert_log(str(info))


def init_logger(app):
    global logger
    logger = LoggerPrinter(app)
    return logger


def isdicomfile(thefile):
    ret = False
    with open(thefile, 'rb') as f:
        cont = f.read(132)
        cont = cont.lower()
        if str(cont).find('dicm') > -1:
            ret = True
    return ret


def getsopinstanceuid():
    sopid = str(uuid.uuid1()).replace("-", '.')
    sopid = sopid.replace('a', '1')
    sopid = sopid.replace('b', '2')
    sopid = sopid.replace('c', '3')
    sopid = sopid.replace('d', '4')
    sopid = sopid.replace('e', '5')
    sopid = sopid.replace('f', '6')
    if len(sopid) % 2 == 1:
        sopid += '0'
    return sopid


def readDicomFile_onefile(thefile):
    if os.path.exists(thefile):
        if isdicomfile(thefile):
            try:
                ds = dicomio.read_file(thefile)
                return ds
            except:
                logger.warning(traceback.format_exc())
                logger.warning("读取文件失败：%s" % thefile)
        else:
            logger.error(('Invalid DICOM File:{0}'.format(thefile)))
    else:
        logger.error("file does not exist:" + thefile)
    return False


def search_tag_onefile(thefile, taglist):
    if isdicomfile(thefile):
        try:
            tagsinfolist = []
            ds = dicomio.read_file(thefile)
            for elem in ds.iterall():
                if elem.tag in taglist:
                    tagsinfolist.append(
                        u'Tag={0:0>8x},name={1}, Value={2}, Type={3}'.format(elem.tag, elem.name, elem.value, elem.VR))
            tagsinfo = '\n'.join(tagsinfolist)
            return tagsinfo
        except:
            logger.warning(traceback.format_exc())
            logger.warning("读取文件失败：%s" % thefile)
    else:
        logger.error(('Invalid DICOM File:{0}'.format(thefile)))


# def get_file_list(src):
#     g_fileList = []
#     for dirPath, dirs, files in os.walk(src):
#         for theFile in files:
#             the_tmp_file_path = dirPath + "\\" + theFile
#             if isdicomfile(the_tmp_file_path):
#                 g_fileList.append(dirPath + "\\" + theFile)
#     return g_fileList


def updatetag_all_dcm_file(folder, tag, function):
    for dirPath, dirs, files in os.walk(folder):
        for theFile in files:
            the_tmp_file_path = dirPath + "\\" + theFile
            if isdicomfile(the_tmp_file_path):
                # logger.info('更新文件: %s' % the_tmp_file_path)
                function(the_tmp_file_path, copy.deepcopy(tag))


def get_first_file(src):
    for dirPath, dirs, files in os.walk(src):
        for theFile in files:
            the_tmp_file_path = dirPath + "\\" + theFile
            if isdicomfile(the_tmp_file_path):
                return the_tmp_file_path
    return None


def is_Chinese(word):
    for ch in word:
        # print ord(ch)
        if ch >= u'一' and ch <= u'龥':
            return True
    return False


def getvalueFromVR(vr, thevalue):
    if vr == 'DS' or vr == 'FL' or vr == 'FD' or vr == 'OF':
        if thevalue.find('\\'):
            valuelist = thevalue.split('\\')
            newlist = []
            for x in valuelist:
                newlist.append(float(x))
            ret = newlist
        else:
            ret = float(thevalue)
    # SL - Signed Long
    # 有符号长型	有符号二进制整数
    # UL - Unsigned Long 无符号长型	无符号二进制整数，长度 32 比特
    elif vr == 'UL' or vr == 'SL' or vr == 'SS' or vr == 'US' or vr == 'IS':
        # ds[tag].value = int(thevalue,2)
        ret = int(thevalue, 10)
        # print 'hello'
    else:
        ret = thevalue
    return ret


class DoEvent(threading.Thread):
    def __init__(self, open_type, open_path, tag_dict):
        threading.Thread.__init__(self)
        self.open_type = open_type
        self.open_path = open_path
        self.tag_dict = tag_dict

    def run(self):
        logger.info('开始执行, 请稍等')
        starttime = time.time()
        # try:
        self.do_event()
        # except:
        # logger.error(traceback.format_exc())
        endtime = time.time()
        logger.info('执行结束')
        logger.info('用时：%s' % (endtime - starttime))
        logger_end()

    def do_event(self):
        pass


class UpdateTag(DoEvent):
    def do_event(self):
        logger.info('开始更新tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            updatefile(self.open_path, self.tag_dict)
        else:
            updatedir(self.open_path, self.tag_dict)
        logger.info('更新tag结束')


class UpdateChildTag(DoEvent):
    def do_event(self):
        logger.info('开始更新子tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            updatechildtagfile(self.open_path, self.tag_dict)
        else:
            updatechilddir(self.open_path, self.tag_dict)
        logger.info('更新子tag结束')


class AddTag(DoEvent):
    def do_event(self):
        logger.info('开始添加tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            addtagfile(self.open_path, self.tag_dict)
        else:
            addtagdir(self.open_path, self.tag_dict)
        logger.info('添加tag结束')


class AddChildTag(DoEvent):
    def do_event(self):
        logger.info('开始添加子tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            addchildtagfile(self.open_path, self.tag_dict)
        else:
            addchildtagdir(self.open_path, self.tag_dict)
        logger.info('添加子tag结束')


class DeleteChildTag(DoEvent):
    def do_event(self):
        logger.info('开始删除子tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            deletechildtagfile(self.open_path, self.tag_dict)
        else:
            deletechildtagdir(self.open_path, self.tag_dict)
        logger.info('删除子tag结束')


class NewStudy(DoEvent):
    def do_event(self):
        logger.info('开始生成新检查')
        if self.open_type == 1:
            new_study_file(self.open_path)
        else:
            new_study_dir(self.open_path)
        logger.info('生成新检查结束')


class AnonymousData(DoEvent):
    def do_event(self):
        logger.info('开始匿名数据')
        if self.open_type == 1:
            anonymous_file(self.open_path, 'Anonymous')
        else:
            anonymous_dir(self.open_path, 'Anonymous')
        logger.info('匿名数据结束')


class CustomAnonymous(DoEvent):
    def do_event(self):
        logger.info('开始匿名数据')
        if self.open_type == 1:
            anonymous_file(self.open_path, self.tag_dict)
        else:
            anonymous_dir(self.open_path, self.tag_dict)
        logger.info('匿名数据结束')


class NewCopyStudy(DoEvent):
    def do_event(self):
        logger.info('开始复制并生成新检查')
        if self.open_type == 1:
            new_copy_study_file(self.open_path, self.tag_dict)
        else:
            new_copy_study_dir(self.open_path, self.tag_dict)
        logger.info('复制并生成新检查结束')


class DeleteTag(DoEvent):
    def do_event(self):
        logger.info('开始删除tag：%s' % str(self.tag_dict))
        if self.open_type == 1:
            deletetagfile(self.open_path, self.tag_dict)
        else:
            deletetagdir(self.open_path, self.tag_dict)
        logger.info('删除tag结束')


class CopyData(DoEvent):
    def do_event(self):
        logger.info('开始复制数据')
        if self.open_type == 1:
            copy_file(self.open_path)
        else:
            copy_dir(self.open_path)
        logger.info('复制数据结束')


def anonymous_dir(folder, patient_name):
    studyinstanceuid_dict = {}
    seriesinstanceuid_dict = {}
    for dirPath, dirs, files in os.walk(folder):
        for theFile in files:
            file = dirPath + "\\" + theFile
            if isdicomfile(file):
                ds = dicomio.read_file(file)
                old_studyinstanceuid = ds[0x0020, 0x000d].value
                old_seriesinstanceuid = ds[0x0020, 0x000e].value
                if old_studyinstanceuid not in studyinstanceuid_dict:
                    studyinstanceuid_dict[old_studyinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000d].value = studyinstanceuid_dict[old_studyinstanceuid]
                if old_seriesinstanceuid not in seriesinstanceuid_dict:
                    seriesinstanceuid_dict[old_seriesinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000e].value = seriesinstanceuid_dict[old_seriesinstanceuid]
                ds[0x0008, 0x0018].value = getsopinstanceuid()
                ds[0x0010, 0x0010].value = patient_name
                if int('00081070', 16) in ds.keys():
                    ds[0x0008, 0x1070].value = 'Anonymous'
                if int('00100030', 16) in ds.keys():
                    ds[0x0010, 0x0030].value = ''
                ds.save_as(file)
            else:
                logger.warning("file does not exist/not a dicom file:" + file)


def anonymous_file(file, patient_name):
    if isdicomfile(file):
        ds = dicomio.read_file(file)
        ds[0x0020, 0x000d].value = getsopinstanceuid()
        ds[0x0020, 0x000e].value = getsopinstanceuid()
        ds[0x0008, 0x0018].value = getsopinstanceuid()
        ds[0x0010, 0x0010].value = patient_name
        ds[0x0008, 0x1070].value = 'Anonymous'
        ds[0x0010, 0x0030].value = ''
        ds.save_as(file)
    else:
        logger.warning("file does not exist/not a dicom file:" + file)


def new_study_dir(folder):
    studyinstanceuid_dict = {}
    seriesinstanceuid_dict = {}
    for dirPath, dirs, files in os.walk(folder):
        for theFile in files:
            file = dirPath + "\\" + theFile
            if isdicomfile(file):
                ds = dicomio.read_file(file)
                old_studyinstanceuid = ds[0x0020, 0x000d].value
                old_seriesinstanceuid = ds[0x0020, 0x000e].value
                if not old_studyinstanceuid in studyinstanceuid_dict:
                    studyinstanceuid_dict[old_studyinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000d].value = studyinstanceuid_dict[old_studyinstanceuid]
                if not old_seriesinstanceuid in seriesinstanceuid_dict:
                    seriesinstanceuid_dict[old_seriesinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000e].value = seriesinstanceuid_dict[old_seriesinstanceuid]
                ds[0x0008, 0x0018].value = getsopinstanceuid()
                ds.save_as(file)
            else:
                logger.warning("file does not exist/not a dicom file:" + file)


def new_study_copy_dir(folder, index):
    studyinstanceuid_dict = {}
    seriesinstanceuid_dict = {}
    for dirPath, dirs, files in os.walk(folder):
        for theFile in files:
            file = dirPath + "\\" + theFile
            if isdicomfile(file):
                ds = dicomio.read_file(file)
                old_studyinstanceuid = ds[0x0020, 0x000d].value
                old_seriesinstanceuid = ds[0x0020, 0x000e].value
                if not old_studyinstanceuid in studyinstanceuid_dict:
                    studyinstanceuid_dict[old_studyinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000d].value = studyinstanceuid_dict[old_studyinstanceuid]
                if not old_seriesinstanceuid in seriesinstanceuid_dict:
                    seriesinstanceuid_dict[old_seriesinstanceuid] = getsopinstanceuid()
                ds[0x0020, 0x000e].value = seriesinstanceuid_dict[old_seriesinstanceuid]
                ds[0x0008, 0x0018].value = getsopinstanceuid()
                ds[0x0010, 0x0010].value = str(ds[0x0010, 0x0010].value)+str(index)
                ds[0x0010, 0x0020].value = str(ds[0x0010, 0x0020].value)+str(index)
                ds.save_as(file)
            else:
                logger.warning("file does not exist/not a dicom file:" + file)


def new_study_file(file):
    if isdicomfile(file):
        ds = dicomio.read_file(file)
        ds[0x0020, 0x000d].value = getsopinstanceuid()
        ds[0x0020, 0x000e].value = getsopinstanceuid()
        ds[0x0008, 0x0018].value = getsopinstanceuid()
        ds.save_as(file)
    else:
        logger.warning("file does not exist/not a dicom file:" + file)


def copy_file(file):
    target_file = os.path.splitext(file)[0] + '_bkp' + os.path.splitext(file)[1]
    logger.info('数据复制为：%s' % target_file)
    shutil.copyfile(file, target_file)


def copy_dir(predir):
    target_dir = predir + '_bkp'
    logger.info('数据复制为：%s' % target_dir)
    shutil.copytree(predir, target_dir)


def new_copy_study_file(file, count):
    for i in range(int(count)):
        logger.info('生成第%s个检查' % str(i + 1))
        target_file = os.path.splitext(file)[0] + str(i + 1) + os.path.splitext(file)[1]
        shutil.copyfile(file, target_file)
        new_study_file(target_file)


def new_copy_study_dir(predir, count):
    for i in range(int(count)):
        logger.info('生成第%s个检查' % str(i + 1))
        target_dir = predir + str(i + 1)  # source_path 是创建子文件夹(因为复制文件夹 不 复制源文件夹目录）
        shutil.copytree(predir, target_dir)
        new_study_copy_dir(target_dir, i+1)


def updatedir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, updatefile)


def updatefile(dcm_file, tag_dict):  # tag_dict:{tag:value}
    if isdicomfile(dcm_file):
        try:
            ds = dicomio.read_file(dcm_file)
            for tag, value in tag_dict.items():
                ds[tag].value = getvalueFromVR(ds[tag].VR, value)
            ds.save_as(dcm_file)
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
    else:
        logger.warning("file does not exist/not a dicom file:" + dcm_file)


def addtagdir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, addtagfile)


def addtagfile(dcm_file, tag_dict):  # tag_dict: {tag:{'type':VR,'value':value}}
    if isdicomfile(dcm_file):
        try:
            os.chmod(dcm_file, stat.S_IREAD | stat.S_IWRITE)
            ds = dicomio.read_file(dcm_file)  # plan dataset
            for tag, info in tag_dict.items():
                VR = info['vr']
                if VR == 'SQ':
                    value = sequence.Sequence()
                else:
                    value = getvalueFromVR(VR, info['value'])
                ds.add_new(tag, VR, value)
            ds.save_as(dcm_file)
            return True
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
            return False
    else:
        logger.warning('file does not exist/maybe not dicom file:{0}'.format(dcm_file))


def addchildtagdir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, addchildtagfile)


def addchildtagfile(dcm_file, tag_dict):
    if isdicomfile(dcm_file):
        try:
            os.chmod(dcm_file, stat.S_IREAD | stat.S_IWRITE)
            ds = dicomio.read_file(dcm_file)
            i = 1
            for elem in ds.iterall():
                if elem.tag == tag_dict['parent_tag']:
                    if i == tag_dict['parent_index']:
                        ds2 = Dataset()
                        de = DataElement(tag_dict['child_tag'], tag_dict['child_VR'], tag_dict['child_value'])
                        ds2.add(de)
                        if not elem.value:
                            elem.value = sequence.Sequence()
                        elem.value.append(ds2)
                    i += 1
            ds.save_as(dcm_file)
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
            return False
    else:
        logger.warning('file does not exist/maybe not dicom file:{0}'.format(dcm_file))


def deletechildtagdir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, deletechildtagfile)


def deletechildtagfile(dcm_file, tag_dict):
    if isdicomfile(dcm_file):
        try:
            os.chmod(dcm_file, stat.S_IREAD | stat.S_IWRITE)
            ds = dicomio.read_file(dcm_file)
            i = 1
            for elem in ds.iterall():
                if elem.tag == tag_dict['parent_tag']:
                    if i == tag_dict['parent_index']:
                        j = 1
                        is_get = False
                        for x in range(len(elem.value)):
                            list_x = list(elem.value[x])
                            for d_elem in list_x:
                                if d_elem.tag == tag_dict['child_tag']:
                                    if tag_dict['child_index'] == j:
                                        is_get = True
                                        break
                                    j += 1
                            if is_get:
                                break
                        if is_get:
                            if len(list_x) == 1:
                                del elem.value[x]
                            else:
                                del elem.value[x][tag_dict['child_tag']]
                    i += 1
            ds.save_as(dcm_file)
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
            return False
    else:
        logger.warning('file does not exist/maybe not dicom file:{0}'.format(dcm_file))


def updatechilddir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, updatechildtagfile)


def updatechildtagfile(dcm_file, tag_dict):
    if isdicomfile(dcm_file):
        try:
            os.chmod(dcm_file, stat.S_IREAD | stat.S_IWRITE)
            ds = dicomio.read_file(dcm_file)
            i = 1
            for elem in ds.iterall():
                if elem.tag == tag_dict['child_tag']:
                    if i == tag_dict['child_index']:
                        elem.value = tag_dict['child_value']
                    i += 1
            ds.save_as(dcm_file)
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
            return False
    else:
        logger.warning('file does not exist/maybe not dicom file:{0}'.format(dcm_file))


def deletetagdir(folder, tag_dict):
    updatetag_all_dcm_file(folder, tag_dict, deletetagfile)


def deletetagfile(dcm_file, tag_dict):
    if isdicomfile(dcm_file):
        try:
            os.chmod(dcm_file, stat.S_IREAD | stat.S_IWRITE)
            ds = dicomio.read_file(dcm_file)
            ischanged = False
            for tag in tag_dict:
                ischanged = True
                del ds[tag]
            if ischanged:
                ds.save_as(dcm_file)
        except:
            logger.warning(traceback.format_exc())
            logger.warning("修改文件失败：%s" % dcm_file)
            return
    else:
        logger.warning('file does not exist/maybe not dicom file:{0}'.format(dcm_file))


def logger_end():
    # global logger
    logger.info('=================end=================\n')

