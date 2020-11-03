import logging
import os
import bs4
from constants import *
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import aiohttp
import asyncio
from urllib import parse

COOKIE = os.environ.get("ALLEN_COOKIE")
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
		link.name = tit
		
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

