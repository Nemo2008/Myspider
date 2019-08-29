# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""
import csv
import re
#from imp import reload

import urllib2
#import urllib.request

import random
from bs4 import BeautifulSoup

import sys

#from numpy.core import unicode

reload(sys)
sys.setdefaultencoding("utf-8")

#import xlsxwriter
#import datetime
#import time
import xlrd
import xlwt


# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

# 北京区域列表
regions = [u"xichen"]
#subregion = [u"tiantan",u"baizhifang1",u"changchunjie",u"fuchengmen",u"guanganmen",u"tianningsi1",u"xidan",u"xuanwumen12",u"youanmennei11",u"yuetan"]
subregion = [u"tiantan"]

def getSoup(url):

        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        return BeautifulSoup(plain_text)


def getAllDistrictInArea(url,region,subregion):

    soup = getSoup(url)
    d = "d=" + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    exec (d)
    total_pages = d['totalPage']
    xiaoqu_info = []

    for i in range(total_pages):
        url_page = u"%s/pg%d" %(url, i)
        page_soup=getSoup(url_page)
        xiaoqu_list = page_soup.findAll('li', {'class': 'clear xiaoquListItem'})
        for j in range(len(xiaoqu_list)):
            tmp = []
            xiaoqu_name = xiaoqu_list[j].find('div',{'class': 'title'}).select('div a')[0].get_text()
            xiaoqu_link = xiaoqu_list[j].find('div',{'class': 'title'}).select('div a')[0].attrs['href']
            xiaoqu_code = xiaoqu_link[-14:-1]
            chengjiao_link = u"%s%s/" %("https://bj.lianjia.com/chengjiao/c",xiaoqu_code)
            saleprice = xiaoqu_list[j].find('div',{'class': 'totalPrice'}).select('span')[0].get_text()
            tmp.append(xiaoqu_name)
            tmp.append(xiaoqu_link)
            tmp.append(chengjiao_link)
            tmp.append(saleprice)
          #  tmp.append(salecount)
            tmp.append(region)
            tmp.append(subregion)
            xiaoqu_info.append(tmp)

    filename = u"%s_%s.xls" %(region,subregion)
  #  writeCVS_xiaoqu(filename,xiaoqu_info)
    writeXLS(filename, subregion, [u'小区名称',u'小区链接',u'小区成交链接',u'目前价格',u'大区',u'小区'], xiaoqu_info)
    print u"爬下了 %s 区全部的小区信息" % subregion


def writeCVS_xiaoqu(filename,info):
    with open(filename,'w') as fp:
        writef =csv.writer(fp)
        writef.writerow(['小区名称','小区链接','小区成交链接','目前价格','大区','小区'])
        for item in info:
            writef.writerow([c for c in item])


def getAllHistoryInfoByHouseCode(xiaoqu_chengjiao_url,xiaoqu_name,region,subregion):
    soup = getSoup(xiaoqu_chengjiao_url)
    d = "d=" + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    exec (d)
    total_pages = d['totalPage']
    house_info = []

    for i in range(1,total_pages):
        url_page = u"%s/pg%d%s" % ("https://bj.lianjia.com/chengjiao/",i,xiaoqu_chengjiao_url[-15:-1])
        page_soup = getSoup(url_page)
        house_list = page_soup.findAll('div', {'class': 'info'})
        for j in range(len(house_list)):
            tmp = []
            house_name = house_list[j].find('div', {'class': 'title'}).select('div a')[0].get_text()
            house_link = house_list[j].find('div', {'class': 'title'}).select('div a')[0].attrs['href']
   #         print "i = %d j = %d house_name = %s house_link = %s" %(i,j,house_name,house_link)
            saleprice = house_list[j].find('div', {'class': 'totalPrice'}).select('span')[0].get_text()
            if (house_list[j].find('div', {'class': 'unitPrice'}).select('span') != []):
                unitprice = house_list[j].find('div', {'class': 'unitPrice'}).select('span')[0].get_text()
            else:
                unitprice = 0
            if (house_list[j].find('div', {'class': 'dealDate'})!= []):
                dealDate = house_list[j].find('div', {'class': 'dealDate'}).get_text()
            else:
                dealDate = 0
            tmp.append(xiaoqu_name)
            tmp.append(house_name)
            tmp.append(house_link)
            tmp.append(saleprice)
            tmp.append(unitprice)
            tmp.append(dealDate)
            tmp.append(region)
            tmp.append(subregion)
            house_info.append(tmp)

    filename = u"%s_%s_%s_deal.xls" %(region,subregion,xiaoqu_name)
    writeXLS(filename, xiaoqu_name, [u'小区名称', u'房子名称', u'房子链接', u'总价', u'单价', u'成交时间', u'大区', u'小区'], house_info)
    print u"爬下了 %s 区历史成交小区信息" % xiaoqu_name

def writeCVS_xiaoqu_chengjiao(info):
    with open('xiaoqu_chengjiao.csv','w') as fp:
        writef =csv.writer(fp)
        writef.writerow([u'小区名称',u'房子名称',u'房子链接',u'总价',u'单价',u'成交时间',u'大区',u'小区'])
        for item in info:
            writef.writerow([c for c in item])


def writeXLS(filename,mysheetname,titles,bodys):

    file = xlwt.Workbook()
    mySheet = file.add_sheet(mysheetname, cell_overwrite_ok=True)

    j = 0
    for title in titles:
        mySheet.write(0,j,title)
        j = j + 1

    j = 1
    for items in bodys:
        i = 0
        for item in items:
            mySheet.write(j,i,item)
            i = i + 1
        j = j + 1

    file.save(filename)


def readXLS(filename,mysheetname):

    x1 = xlrd.open_workbook(filename)
    sheet1 = x1.sheet_by_name(mysheetname)
    row_num = sheet1.nrows

    house_info = []
    for i in range(1,sheet1.nrows):
  #      print sheet1.cell_value(i,3)
 #       print sheet1.cell_type(i,3)
#        if (sheet1.cell_value(i,3).find('暂无') < 0):
        tmp = []
        tmp.append(sheet1.cell_value(i, 0))
        tmp.append(sheet1.cell_value(i, 2))
        tmp.append(sheet1.cell_value(i, 4))
        tmp.append(sheet1.cell_value(i, 5))
        house_info.append(tmp)

 #   print row_num
 #   print i
 #   print house_info
    return house_info
#    print 'sheet_names:', x1.sheet_names()  # 获取所有sheet名字
#    print 'sheet_number:', x1.nsheets  # 获取sheet数量
#    print 'sheet_object:', x1.sheets()  # 获取所有sheet对象
#    print 'By_name:', x1.sheet_by_name("tianningsi1")  # 通过sheet名查找
#    print 'By_index:', x1.sheet_by_index(3)  # 通过索引查找

    # 获取sheet的汇总数据
#    sheet1 = x1.sheet_by_name("tianningsi1")
#   print "sheet name:", sheet1.name   # get sheet name
#   print "row num:", sheet1.nrows  # get sheet all rows number
#   print "col num:", sheet1.ncols  # get sheet all columns number

district_url = u"https://bj.lianjia.com/xiaoqu/taoranting1"
xiaoqu_chengjiao_url = u"https://bj.lianjia.com/chengjiao/c1111027378190/"

if __name__ == "__main__":

 #   for region in subregion:
 #      xiaoqu_district_url = u"https://bj.lianjia.com/xiaoqu/%s" %(region)
 #      getAllDistrictInArea(xiaoqu_district_url,u"xichen",region)
 #    house_info = readXLS(u"house_data/xichen_xiaoqu_8.xls", u"baizhifang1")

     for region in subregion:
        house_info = readXLS(u"house_data/xichen_xiaoqu_8.xls",region)
        for info in house_info:
           getAllHistoryInfoByHouseCode(info[1],info[0],info[2],info[3])


   #  getAllHistoryInfoByHouseCode(xiaoqu_chengjiao_url,u"凌云居",u"xichen",u"niujie")


