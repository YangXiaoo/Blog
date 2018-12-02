# coding:UTF-8
import urllib2
import json

def get_area(ip):
    url = 'http://ip-api.com/json/' + str(ip)
    urlobject = urllib2.urlopen(url)  
    urlcontent = urlobject.read()  
    res = json.loads(urlcontent)
    return res

if __name__ == '__main__':
	# ret = get_area('110.84.0.129')
	url = 'http://ip-api.com/json/110.84.0.129'
	# 访问url地址, urlobject是<type 'instance'>对象；
	urlobject = urllib2.urlopen(url)

	# url地址访问后的返回值；urlcontent类型为字符串；
	# urlcontent = '{
	#   "ip":"172.25.254.250","country_code":"","country_name":"",
	#   "region_code":"","region_name":"","city":"","zip_code":"",
	#   "time_zone":"","latitude":0,"longitude":0,"metro_code":0
	#   }'
	# latitude: 纬度
	# longitude： 经度
	urlcontent = urlobject.read()

	# 很明显字符串的信息不好处理的， 那么json模块可以帮忙的；
	res = json.loads(urlcontent)

	print(res)