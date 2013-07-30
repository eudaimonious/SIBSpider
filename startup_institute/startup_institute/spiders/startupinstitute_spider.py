#! -*- coding: utf-8 -*-

"""
By Margaret Scott
"""
from scrapy.http import Request, FormRequest
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector


class StartupInstituteSpider(BaseSpider):
    name = "startupinstitute"
    allowed_domains = ["bostonlabs.startupinstitute.com", "docs.google.com"]
    start_urls = ["http://bostonlabs.startupinstitute.com"]

    def parse(self, response):
        return [FormRequest.from_response(response,
                    formdata={'log': 'eudaimonious@gmail.com', 'pwd': 'sib'},
                    callback=self.after_login)]

    def after_login(self, response):
        """
        Parse track pages and extract lab links.

        """
        # check login succeed before going on
        if "Welcome" not in response.body:
            self.log("Login failed")
            return

        # continue scraping with authenticated session...
        self.log('Parsing Site')
        selector = HtmlXPathSelector(response)
        tracks = selector.select('//*[@id="menu1"]/li/a/@href').extract()
        for track in tracks:
            self.log('Found track url: %s' % track)
            yield Request(track, callback = self.parseFullTrack)

    def parseFullTrack(self, response):
        """
        Parse track page and extract links of lab pages.
        """
        self.log('Parsing a track...')
        selector = HtmlXPathSelector(response)
        urls = selector.select('//h2/a/@href').extract()
        for url in urls:
            self.log('Found lab url: %s' % url)
            yield Request(url, callback = self.parseLab)

    def parseLab(self, response):
        """
        Parse lab page and extract links of source docs.

        """
        self.log('Parsing Labs')
        selector = HtmlXPathSelector(response)
        links = selector.select('//iframe/@src').extract()
        for link in links:
            self.log('Found source link: %s' % link)
            yield Request(link, callback = self.saveSource)

    def saveSource(self, response):
        """
        Save source docs.

        """
        selector = HtmlXPathSelector(response)
        #Find the doc's title
        t = selector.select('//head/title/text()').extract()
        t = t[0]
        t = t.encode('ascii','ignore')
        t = t.replace('/', '-').replace('\\', '-')
        t += ".html"
        self.log('Saving: %s' % t)
        #Save the doc with the title
        f=open(t, 'wb')
        f.write(response.body)
        f.close
        self.log('Saved: %s' % t)
        #Download

