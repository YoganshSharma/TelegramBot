import logging

import bs4
from constants import *
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import ujson 
import aiohttp
import asyncio
from urllib import parse


import sys
prct = 0
COOKIE = "Ibah0V--SAp6TdWTrFFCLA9Aj0KISILM40W0FcaTUPKag1B_k9cUyFLjFIk7C0s-i47UwP9HgH3AZjFWkbNmDZP1Ex6YvqXEWY85WtN_eEAvc0xVl1KhOEeBb8wbzluARpEQ4m8aP66KKo1DYYby2H2ooQ5sJnAxYVkxiXywMS7QFoiDNE4OBogg3NvZGgQao0undP1TSbeoBXXNX8zMM0hmZuv6SJa2zZJ76ddT0WFNoP7F31KN6dC6A5hJZGExgYg_7l485H1d5heRiSt69OrX41Ie44PGh4TFxlI1cdmFtRto7DfVAYhKgh11WYvhSqVNI9EAtlJ8LduzGv3OcOduK5H2VvqQ19gPZ8MjhvY81PgAggF8mCB9ijUh9PWk1YHb22f_ftf5cZovvc-GO6bHsMLHxZBP95-a05H5zKL4I9Ucp6Ac_2MDO2jFy-acDWJrK3XCdTxDnA1-ExHSn1--5Sh3JjgG-lqNkf6dPVoPZP6neuNADsSiwHzsStzv8F6qn5LU3LZM2jPyLYlR7AZVmoqwj6MPYBB4QDHXiKO93_ZDqeiazL1rTEiTbJndVPgKgEfKPzxOT_7JaY8QGgVcK0YzxsO-KCTXSz_ry34eaDiqk52qa2powJnji91HfsKsw49GvsqDiJq1iP0KFZcMw0qchHEq7F_zCv2PGV0p16a-0vLJF4FVXlyhbR8tvzVNv1XZpH7wyWhRlZ28zlGhxsa2ZNN3mkZGWw0QTKaNbGJ6h1nccxfGL2YwtcGz6LV7-q3Ug-TT5-tyLDT0L8nE928OTkG4oPKQBJBptqrJrZIjIGKX9d_9pHLit-bw8HuCiHOQ5oSKMsseDE4mc9vlKIE"
BASE = 'https://student.allendigital.in'
async def open_browser(url,cookie):
	async with aiohttp.request("GET",url,cookies={'.allendigital.in':cookie}) as resp:
		data = await resp.read()
	
	sp = BeautifulSoup(str(data),'lxml')
	return sp

class Link:
	url = ""
	path = ""
	name = ""
	ext = ".mp4"
	linkType = "url"
	def __str__(self):
		return str(self.comp())
	def __repr__(self) -> str:
		return self.__str__()
	def comp(self):
		return {self.name:parse.quote(self.url)}

class Scrap:
	def __init__(self) -> None:
		self.downloadLinks = []
	async def get_soup(self,url = None):
		if not url:
			url = self.url
		self.soup = None
		try: 
			print("Getting Soup ", url)
			self.soup = await open_browser(url,COOKIE)
		except:
			logging.error(f"Unable to get {url}",exc_info = True)
			return
		return self.soup
	async def all(self,reverse = True,dwntype = LIVE):

		if dwntype==LIVE:
			url = LIVE_URL
		else:
			url = DIGITAL_URL

		self.soup = await self.get_soup(url)
		links = self.soup.find_all("div",class_ = "tile-box")
		if len(links)<=0:
			print("noclass")
			return
		if reverse:
			links = links[::-1]
		urls = []
		for link in links:
			
			url = urljoin(url, link.find('a')["href"])
			if dwntype==LIVE:
				urls.append(self.live(url))
			else:
				
				lnk = Link()
				link:bs4.Tag
				
				lnk.name = link.findChild("div",class_ = "tile-content-wrapper").find_all("small")[-1].get_text().replace("\\r\\n","").strip().replace("|","")
				print(lnk.name,"NAME")
				lnk.url = parse.urlparse(url).path.split("/")[-1]
				lnk.linkType = "data"
				self.downloadLinks.append(lnk)
		
		if dwntype==LIVE:
			await asyncio.gather(*urls)
	async def allDigital(self,reverse = True, download = True,writeLinks = True):
		self.downloadDigital = download
		self.writeLinks = writeLinks
		await self.all(reverse,dwntype = DIGITAL)
		return self.downloadLinks
	async def digital(self, url):
		if not url:
			url = self.url
		try:
			print(url)
			sp = await self.get_soup(url)
			lsts = sp.find_all('div', class_ = 'list-group')
			itms = lsts[0].find_all('a', class_ = 'list-group-item')
			self.downloadLinks = []
			vidpages = []
			ind =1
			for itm in itms:
				vidpages.append(self.digitalModules(itm,url,ind))
				ind += 1
			links = await asyncio.gather(*vidpages)
			
			for link in links:
				self.downloadLinks.append(link)
			return self.downloadLinks
		except:
			return "Class not found"
	async def digitalModules(self,itm,url,ind = 1):
		url = urljoin(url,itm['href'])

		vidpage = await self.get_soup(url)
			
		nam = ''.join(str([text for text in itm.stripped_strings][-1]).replace(' ','').split('\n')[-1]).split('.')[-1].replace('|','_')+'-'+'M'+'0'+str(ind) + '.mp4'

		nam = re.sub(r'\\[a-z]','',nam)
		nam = re.sub(r'\\','',nam)
		nam = re.sub(r'/','',nam)
		lnk = vidpage.find('source')['src']
		link = Link()
		link.url  = urljoin(url,lnk)
		link.name = nam
		return link		
	async def allLive(self,reverse = True):
		print("ALL Live classes")
		await self.all(reverse,dwntype = LIVE)
		return self.downloadLinks
	async def live(self,url = None):
		if not url:
			url = self.url
		sp = await self.get_soup(url)
		url = sp.find('source')['src']
		pgt = sp.find_all('div', id = 'page-title')
				
		tit = ''.join(str(pgt[0].h2.text).replace(' ',''))
		tit = re.sub(r'\\[a-z]','',tit)
		tit = re.sub(r'\\','',tit)
		tit = re.sub(r'/','',tit)
		tit = tit.replace('|','_')
		link = Link()
		link.url  = url
		link.ext = VIDEO_EXT
		link.name = tit
		link.path = LIVE_SAVE_PATH
		
		self.downloadLinks.append(link)
	def material(self,url = None,download = True,writeLinks = True):
		self.downloadLinks = []
		if not url:
			url = self.url
		sp = self.get_soup(url)
		lsts = sp.find_all('div', class_ = 'list-group')
		itms = lsts[0].find_all('a', class_ = 'list-group-item')
		for itm in itms:
			nam = str(itm.text).replace(' ','').split('\n')[-1].split('.')[-1] + '.pdf'
			nam = re.sub(r'\\[a-z]','',nam)
			lnk = itm['href']
			link = Link()
			link.url  = urljoin(url,lnk)
			link.name = nam
			self.downloadLinks.append(link)
		if writeLinks:
			self.save_links()
		if download:
			self.startdown()

