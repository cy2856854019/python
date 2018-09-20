
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, requests, scrapy, json

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,und;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "
} 

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = \
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 "

driver = webdriver.PhantomJS(executable_path="/usr/local/bin/phantomjs", desired_capabilities=dcap)

#get cookies
def get_cookies(url):
    cookie_list = {}
    driver.get(url)
    time.sleep(2)
    
    cookies = driver.get_cookies()
    for co in cookies:
        if co in cookies:
            if co['name'] == '__jsl_clearance' or co['name'] == '__jsluid':
                cookie_list[co['name']] = co['value']
    driver.close()
    return cookie_list
# 爬取各省数据
def spider(ids, session):
    for id in ids:
        url = "http://www.gsxt.gov.cn/affiche-query-area-info-paperall.html?noticeType=11&areaid=100000&noticeTitle=&regOrg=" + id
        
        print(url)
        # 5页
        for i in range(1, 6):
            data = {'draw': i, 'start': (i-1)*10, 'length': 10}
            try:
                response = session.post(url, cookies = cookies, headers = headers, data=data, verify=False)
                res_obj = json.loads(response.text)
            except Exception as e:
                print(e)
            else:
                res_dict = res_obj.get('data', None)
                info_list = []
                if res_dict:
                    # 每页10条
                    for info in res_dict:
                        info_dict = {}
                        info_id = info.get('noticeId')
                        info_title = info.get('noticeTitle')
                        info_content = info.get('noticeContent')
                        info_dict['info_id'] = info_id
                        info_dict['info_title'] = info_title
                        info_dict['info_content'] = info_content.replace('&nbsp;&nbsp;', '').replace('<br />', '')
                        info_list.append(info_dict)
                        print(str(info_dict))
                        
if __name__ == '__main__':

    url = 'http://www.gsxt.gov.cn/index.html'
    session = requests.Session()
    cookies = get_cookies(url)

    url =  'http://www.gsxt.gov.cn/corp-query-entprise-info-xxgg-100000.html'

    try:
        response = session.get(url, cookies = cookies, headers = headers, verify=False)
        ids = scrapy.Selector(response).xpath('//div[@class="label-list"]/div/@id').extract()
        provinces = scrapy.Selector(response).xpath('//div[@class="label-list"]/div/label/text()').extract()
 
        spider(ids, session)
    except Exception as e:
        print(e)
    
    
    