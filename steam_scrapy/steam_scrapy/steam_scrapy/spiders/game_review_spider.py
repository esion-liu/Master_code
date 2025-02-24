import scrapy
from scrapy.selector import Selector
import json
from steam_scrapy.items import *
import re
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup



class SteamSpider(scrapy.Spider):
    name = "steam_main"
    allowed_domains = ["store.steampowered.com", "steamcommunity.com"]
    #English, not-free, Game: exclude: DLC, other softwares and hardwares like steam deck and controller
    start_urls = ["https://store.steampowered.com/search/?category1=998&supportedlang=english&hidef2p=1&filter=globaltopsellers&ndl=1&ignore_preferences=1"]
    # avoid 18+ game age checking
    birth_cookie = {'birthtime' : 1009810801}
    counter = 0


    def parse(self, response):
        print("-- Customer LOG: game: Start Steam Crawling")

        number_of_games = 6113 # 6113 record in 2024-05-08 with an Japan IP
        
        # handle non-infinite scroll games
        game_atags = response.xpath('//*[@id="search_resultsRows"]/a')
        for game_atag in game_atags:
            game_url = game_atag.xpath('@href').get()
            game_price_tag = game_atag.xpath('div[2]/div[4]/div/div/div[2]/div[1]')
            # handle games without a ongoing discount
            if not game_price_tag:
                game_price_tag = game_atag.xpath('div[2]/div[4]/div/div/div/div')
            game_price = game_price_tag.xpath('text()').get()
            game_price = re.findall(r'\d+', game_price.replace(',', ''))[0]

            yield response.follow(game_url, callback=self.game_page_parse, cookies=self.birth_cookie, meta={"price" : game_price})

        # handle infinite scroll games
        for i in range(50, number_of_games, 50):
            url = f'https://store.steampowered.com/search/results/?query&start={i}&count=50&dynamic_data=&sort_by=_ASC&category1=998&supportedlang=english&snr=1_7_7_globaltopsellers_7&hidef2p=1&filter=globaltopsellers&infinite=1'
            yield response.follow(url, callback=self.game_list_ajax_parse)
            

    def game_list_ajax_parse(self, response):
        json_data = json.loads(response.text)
        html_data = json_data["results_html"]
        selector = Selector(text=html_data)
        game_atags = selector.xpath(".//a")
        
        for game_atag in game_atags:
            game_url = game_atag.xpath('@href').get()
            game_price_tag = game_atag.xpath('div[2]/div[4]/div/div/div[2]/div[1]')
            if not game_price_tag:
                game_price_tag = game_atag.xpath('div[2]/div[4]/div/div/div/div')
            game_price = game_price_tag.xpath('text()').get()
            game_price = re.findall(r'\d+', game_price.replace(',', ''))[0]
            
            yield response.follow(game_url, callback=self.game_page_parse, cookies=self.birth_cookie, meta={"price" : game_price})
    

    def game_page_parse(self, response):

        try:
            print(response.url)
            try:
                review_summary = response.xpath('//*[@id="userReviews"]/div[2]/div[2]/span[3]/text()').get().strip()
                numbers = re.findall(r'\d+', review_summary.replace(',', ''))
                if len(numbers) < 2:
                    review_summary = response.xpath('//*[@id="userReviews"]/div[2]/div[2]/span[4]/text()').get().strip()
                    numbers = re.findall(r'\d+', review_summary.replace(',', ''))
            except Exception as e:
                review_summary = response.xpath('//*[@id="userReviews"]/div[1]/div[2]/span[3]/text()').get().strip()
                numbers = re.findall(r'\d+', review_summary.replace(',', ''))
            number_reviewers = int(numbers[1])
            title = response.xpath('//*[@id="appHubAppName"]/text()').get().strip()
            title = re.sub(r'[^a-zA-Z,:.-_ ]', '', title)
            if number_reviewers <= 1000:
                # if the game contains small number of reviews, ignore it
                print(f"-- Customer LOG: game: {title} have only {number_reviewers} reviews. The data won't be collected")
                return
            
            # check is there are live streaming
            high_light_blocks = len(response.xpath('//*[@id="game_highlights"]/div'))
            #print('-----hlb', high_light_blocks)
            if high_light_blocks == 3:
                # no live
                offset = 0
            else:
                offset = 1
            #print('-----offset', offset)
            positive_rate = numbers[0]
            
            description = response.xpath(f'//*[@id="game_highlights"]/div[{1+offset}]/div/div[2]/text()').get().strip()

            release_date = response.xpath(f'//*[@id="game_highlights"]/div[{1+offset}]/div/div[3]/div[2]/div[2]/text()').get()
            date_obj = datetime.strptime(release_date, "%d %b, %Y")
            release_date = date_obj.strftime("%Y-%m-%d")

            developer = response.xpath('//*[@id="developers_list"]/a/text()').get()
            publisher = response.xpath(f'//*[@id="game_highlights"]/div[{1+offset}]/div/div[3]/div[4]/div[2]/a/text()').get()


            user_atags = response.xpath('//*[@id="glanceCtnResponsiveRight"]/div[2]/div[2]/a')
            user_tags = []
            for user_atag in user_atags:
                user_tags.append(user_atag.xpath('text()').get().strip())

            genes_atags = response.xpath('//*[@id="genresAndManufacturer"]/span/a')
            genes_tags = []
            for genes_atag in genes_atags:
                genes_tags.append(genes_atag.xpath('text()').get().strip())

            price = response.meta["price"]

            game = GameItem(name=title,
                            description=description,
                            positive_rate=positive_rate,
                            release_date=release_date,
                            developer=developer,
                            publisher=publisher,
                            tags=user_tags,
                            genes=genes_tags,
                            price=price)
            
            yield game

            print(f'-- Customer LOG: game {title} recorded, going to record its reviews')
            game_id = re.search(r'/app/(\d+)/', str(response.url)).group(1)

            review_url = f'https://steamcommunity.com/app/{game_id}/reviews/?browsefilter=mostrecent&snr=1_5_100010_&p=1&filterLanguage=english'

            yield response.follow(review_url, callback=self.review_page_parse, cookies=self.birth_cookie, meta={"game_name" : title})
            
        except Exception as e:
            print(e)
            #print('Game Package Ignored: ', response.url)

    def review_page_parse(self, response):
        #handle non-infinite scroll reviews
        review_divs = response.css('div.apphub_Card')
        for review_div in review_divs:
            try:
                review_item = GameReview()

                review_item['game_name'] = response.meta['game_name']

                review_item['recommended'] = review_div.css('div.title::text').get().strip() == 'Recommended'
                review_item['time_played'] = review_div.css('div.hours::text').get().strip()
                review_item['time_played'] = re.findall(r'\d+\.\d+|\d+', review_item['time_played'].replace(',', ''))[0]
                text_div = review_div.css('div.apphub_CardTextContent').get()
                #print(text_div)
                soup = BeautifulSoup(text_div, 'html.parser')
                for sub_div in soup.find_all("div", attrs={"class": "date_posted"}):
                    sub_div.decompose()
                for br in soup.find_all("br"):
                    br.replace_with(" ")
                
                review_text = soup.get_text(strip=True)
                if review_text.startswith('Early Access Review'):
                    review_item['early_access'] = True
                    review_text = review_text[19:]
                else:
                    review_item['early_access'] = False
                review_item['review_text'] = review_text

                review_item['reviewer_name'] = review_div.css('.apphub_CardContentAuthorName a::text').get().strip()

                funny_helpful_div = review_div.css('div.found_helpful').get()
                soup = BeautifulSoup(funny_helpful_div, 'html.parser')
                for sub_div in soup.find_all("div", attrs={"class": "review_award_aggregated"}):
                    sub_div.decompose()
                for br in soup.find_all("br"):
                    br.replace_with(" ")
                temp = soup.get_text(strip=False)
                temp = temp.strip()
                review_item['number_helpful'], review_item['number_funny'] = self.parse_review_stats(temp)

                #send to pipeline for database saving
                yield review_item
            
            except Exception as e:
                print('-- Customer LOG: error msg - ', e)

        #handle infinite scroll reviews
        next_page_form = response.xpath('//*[@id="MoreContentForm1"]') # for default page the id always use id number 1
        ajax_base_url = next_page_form.xpath('@action').get().strip() + '?'
        input_blocks = next_page_form.css('input[type=hidden]')
        for input_block in input_blocks:
            ajax_base_url += input_block.xpath('@name').get().strip()
            ajax_base_url += '='
            ajax_base_url += quote(input_block.xpath('@value').get().strip())
            ajax_base_url += '&'
        ajax_base_url = ajax_base_url[:-1]
        
        yield response.follow(ajax_base_url, self.review_ajax_parse, meta={"pageno" : 1, "game_name" : response.meta['game_name']})
        

    def review_ajax_parse(self, response):
        if (response.meta['pageno'] + 1) % 10 == 0:
            print('-- Customer LOG: Game ', response.meta['game_name'], ' reached page ', str(response.meta['pageno'] + 1))
        # handle new reviews
        review_divs = response.css('div.apphub_Card')
        for review_div in review_divs:
            try:
                review_item = GameReview()

                review_item['game_name'] = response.meta['game_name']

                review_item['recommended'] = review_div.css('div.title::text').get().strip() == 'Recommended'
                review_item['time_played'] = review_div.css('div.hours::text').get().strip()
                review_item['time_played'] = re.findall(r'\d+\.\d+|\d+', review_item['time_played'].replace(',', ''))[0]
                text_div = review_div.css('div.apphub_CardTextContent').get()
                soup = BeautifulSoup(text_div, 'html.parser')
                for sub_div in soup.find_all("div", attrs={"class": "date_posted"}):
                    sub_div.decompose()
                for br in soup.find_all("br"):
                    br.replace_with(" ")
                
                review_text = soup.get_text(strip=True)
                if review_text.startswith('Early Access Review'):
                    review_item['early_access'] = True
                    review_text = review_text[19:]
                else:
                    review_item['early_access'] = False
                review_item['review_text'] = review_text

                review_item['reviewer_name'] = review_div.css('.apphub_CardContentAuthorName a::text').get().strip()

                funny_helpful_div = review_div.css('div.found_helpful').get()
                soup = BeautifulSoup(funny_helpful_div, 'html.parser')
                for sub_div in soup.find_all("div", attrs={"class": "review_award_aggregated"}):
                    sub_div.decompose()
                for br in soup.find_all("br"):
                    br.replace_with(" ")
                temp = soup.get_text(strip=False)
                temp = temp.strip()
                review_item['number_helpful'], review_item['number_funny'] = self.parse_review_stats(temp)

                yield review_item
            except Exception as e:
                print('-- Customer LOG: error msg - ', e)

        formid = '//*[@id="MoreContentForm' + str(response.meta['pageno'] + 1) + '"]'
        next_page_form = response.xpath(formid) # for default page the id always use id number 1
        if not next_page_form:
            print('-- Customer LOG: Game', response.meta['game_name'], ' review collection finished!')
            # if no next page's form, means we have entered the final page, thus, stop
            return
        ajax_base_url = next_page_form.xpath('@action').get().strip() + '?'
        input_blocks = next_page_form.css('input[type=hidden]')
        for input_block in input_blocks:
            ajax_base_url += input_block.xpath('@name').get().strip()
            ajax_base_url += '='
            ajax_base_url += quote(input_block.xpath('@value').get().strip())
            ajax_base_url += '&'
        ajax_base_url = ajax_base_url[:-1]
        
        yield response.follow(ajax_base_url, self.review_ajax_parse, meta={"pageno" : response.meta['pageno'] + 1, "game_name" : response.meta['game_name']})
            





    def parse_review_stats(self, text):
        # Regular expressions to find numbers or "No one"
        helpful_regex = r'(\d+) person[s]? found this review helpful'
        funny_regex = r'(\d+) person[s]? found this review funny'
        
        # Search for numbers of helpful
        helpful_match = re.search(helpful_regex, text)
        if helpful_match:
            helpful_count = int(helpful_match.group(1))
        elif "No one has rated this review as helpful" in text:
            helpful_count = 0
        else:
            helpful_count = 0  # Default to 0 if nothing is mentioned

        # Search for numbers of funny
        funny_match = re.search(funny_regex, text)
        if funny_match:
            funny_count = int(funny_match.group(1))
        elif "No one has rated this review as funny" in text:
            funny_count = 0
        else:
            funny_count = 0  # Default to 0 if nothing is mentioned

        return helpful_count, funny_count


            
"""
params for next page example
<form method="GET" id="MoreContentForm1" name="MoreContentForm1" action="https://steamcommunity.com/app/281990/homecontent/">
			<input type="hidden" name="userreviewscursor" value="AoIIP3Nc8nPHq3c=">
            <input type="hidden" name="userreviewsoffset" value="10">
            <input type="hidden" name="p" value="2">
            <input type="hidden" name="workshopitemspage" value="2">
            <input type="hidden" name="readytouseitemspage" value="2">
            <input type="hidden" name="mtxitemspage" value="2">
            <input type="hidden" name="itemspage" value="2">
            <input type="hidden" name="screenshotspage" value="2">
            <input type="hidden" name="videospage" value="2">
            <input type="hidden" name="artpage" value="2">
            <input type="hidden" name="allguidepage" value="2">
            <input type="hidden" name="webguidepage" value="2">
            <input type="hidden" name="integratedguidepage" value="2">
            <input type="hidden" name="discussionspage" value="2">
            <input type="hidden" name="numperpage" value="10">
            <input type="hidden" name="browsefilter" value="toprated">
            <input type="hidden" name="l" value="english">	
            <input type="hidden" name="appHubSubSection" value="10">
			<input type="hidden" name="browsefilter" value="toprated">
			<input type="hidden" name="filterLanguage" value="default">
			<input type="hidden" name="searchText" value="">
			<input type="hidden" name="maxInappropriateScore" value="100">
			<input type="hidden" name="forceanon" value="1">							
</form>

corrsponding request url:
https://steamcommunity.com/app/281990/homecontent/?userreviewscursor=AoIIP3Nc8nPHq3c%3D&userreviewsoffset=10&p=2&workshopitemspage=2&readytouseitemspage=2&mtxitemspage=2&itemspage=2&screenshotspage=2&videospage=2&artpage=2&allguidepage=2&webguidepage=2&integratedguidepage=2&discussionspage=2&numperpage=10&browsefilter=toprated&browsefilter=toprated&l=english&appHubSubSection=10&filterLanguage=default&searchText=&maxInappropriateScore=100&forceanon=1

"""

         
