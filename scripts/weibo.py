# -*- coding: utf-8 -*-

import urllib.request
import json
import sys
import re

proxy_addr="222.93.0.25:8118"

def use_proxy(url,proxy_addr):
	req=urllib.request.Request(url)
	req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
	proxy=urllib.request.ProxyHandler({'http':proxy_addr})
	opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
	urllib.request.install_opener(opener)
	data=urllib.request.urlopen(req).read().decode('utf-8','ignore')
	return data
	
def get_info(mid):
	url='https://m.weibo.cn/api/statuses/show?id='+mid
	data=use_proxy(url,proxy_addr)
	result=json.loads(data)
	user=result.get('user')
	text=result.get('text')
	return user.get('id'),text,user.get("screen_name")

def get_containerid(url):
	data=use_proxy(url,proxy_addr)
	content=json.loads(data).get('data')
	tab=content.get('tabsInfo').get('tabs')
	for data in tab:
		if(type(data)==type('a')):
			if(tab.get(data).get('tab_type')=='weibo'):
				containerid=tab.get(data).get('containerid')
		else:
			if(data.get('tab_type')=='weibo'):
				containerid=data.get('containerid')
	return containerid
	
def get_weibo(id,num,mid):
	cnt=0
	i=1
	ans=[]
	url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id
	basic_url='https://m.weibo.cn/api/container/getIndex?type=uid&value='+id+'&containerid='+get_containerid(url)+'&page='
	while(cnt<num):
		weibo_url=basic_url+str(i)
		try:
			data=use_proxy(weibo_url,proxy_addr)
			content=json.loads(data).get('data')
			cards=content.get('cards')
			if(len(cards)>0):
				for j in range(len(cards)):
					card_type=cards[j].get('card_type')
					if(card_type==9):
						mblog=cards[j].get('mblog')
						if(mblog.get('mid')==mid):
							continue;
						# attitudes_count=mblog.get('attitudes_count')
						# comments_count=mblog.get('comments_count')
						# created_at=mblog.get('created_at')
						# reposts_count=mblog.get('reposts_count')
						# scheme=cards[j].get('scheme')
						text=mblog.get('text')
						ans.append(text)
						cnt+=1
					if(cnt>=num):
						break
				i+=1
			else:
				break
		except Exception as e:
			print(e)
			pass
	return ans
	
def get_emo(matched):
	return '['+matched.group(1)+']'
	
if __name__=='__main__':
	mid=sys.argv[1]
	cnt=int(sys.argv[2])
	
	filter=re.compile("<[^<>]*>")
	emoti=re.compile("<img alt=\[([^\[\]]*)\] src=\"//h5.sinaimg.cn/m/emoticon/[^<>]*>")
	
	uid,text,username=get_info(mid)
	
	text=emoti.sub(get_emo,text)
	text=filter.sub("",text)
	ret={0:username,1:text}
	
	latest=get_weibo(str(uid),cnt,mid)
	for i in range(len(latest)):
		text=latest[i]
		text=emoti.sub(get_emo,text)
		text=filter.sub("",text)
		ret[i+2]=text
	
	print(json.dumps(ret))