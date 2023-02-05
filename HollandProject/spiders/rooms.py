import scrapy
import json


def parse_delivery_level(string):
    string = string.split("\r\n")
    return string[2].strip()

def parse_avaiablity(string):
    string = string.split("\r\n")
    string = string[2].strip()
    string = string.replace("</div>", "")
    return string.strip()

def parse_title(string):
    string = string.split("\r\n")
    return string[2].strip()

def parse_description(string):
    string[0] = string[0].replace("\r\n" , "").strip()

    return string

def parse_details2(list):
    list_new = []
    for index in list:
        index = index.replace("\r\n", "")
        index = index.replace(" ", "")
        list_new.append(index)
    return list_new

def merge_details(list1, list2):
    merged_list = [str(i) + ": " + str(j) for i, j in zip(list1, list2)]
    return merged_list

def parse_desired_tenant(list):
    for i in range(1, len(list), 2):
        list[i] = list[i].replace("\r\n", "").strip()
        if "-" in list[i]:
            list[i] = list[i].split("-")
            list[i] = list[i][0].strip() + " - " + list[i][1].strip()
            
    if len(list) % 2 == 0:
        for i in range(0, len(list)-1, 2):
            list[i] = list[i] + " : " + list[i+1]
            list[i+1] = ""
    

    list = [x for x in list if x != ""]
    if "\r\n" in list[-1]:
        list.pop()
    return list 

class RoomsSpider(scrapy.Spider):
    name = "rooms"
    allowed_domains = ["www.kamernet.nl"]
    start_urls = ["https://kamernet.nl/huren/kamers-nederland"]
    
    def start_requests(self):
        with open("urls.json", 'r') as f:
            rooms = json.load(f)
        for room in rooms:
            yield scrapy.Request(url=room['room_name'], callback=self.parse)

    def parse(self, response):
        links = response.url
        street_name = response.xpath("//div[@class='h1_line2 truncate']/text()").get()
        types = response.xpath("//div[@class='h1_line1']/text()").get()
        location = response.xpath("//div[@class='h1_line3']/text()").get()
        surface = response.xpath("//div[@class='surface']/text()").get()[1:]
        price = response.xpath("//div[@class='price']/text()").get()[:-1]
        delivery_level = response.xpath("//div[@class='furnishing']").getall()
        delivery_level = parse_delivery_level(delivery_level[0])
        title = response.xpath("//div[@class='col s12 m12 l8 offset-l2 no-padding description']/h2").getall()
        title = parse_title(title[0])

        description = response.xpath("//div[@class='col s12 room-description desc-special-text']/text()").getall()
        description = parse_description(description)

        details1 =  response.xpath("//div[@class='col s6 l3 no-padding-left info-col']/div[2]/div[1]/text()").getall()

        details2 =  response.xpath("//div[@class='col s6 l3 no-padding-left info-col']/div[2]/div[2]/text()").getall()
        details2 = parse_details2(details2)

        details = merge_details(details1, details2)

        availablity = response.xpath("//div[@class='availability']").getall()
        availablity = parse_avaiablity(availablity[0])

        desired_tenant = response.xpath('//div[@class="col s9"]/table/tr/td/text()').getall()
        desired_tenant = parse_desired_tenant(desired_tenant)      

        yield { 'link': links, 'street_name': street_name , 'types': types 
                , 'location': location, 'surface': surface , 'price': price
                , 'delivery_level': delivery_level, 'availablity': availablity
                , 'title': title , 'description': description, 'details': details
                 , 'desired_tenant': desired_tenant}
