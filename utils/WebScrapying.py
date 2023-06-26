import requests
from lxml import html

def cnyes_tags(stock_number):

    url = f"https://www.cnyes.com/twstock/{stock_number}/relation/overview"
    
    # 发送HTTP GET请求获取网页内容
    response = requests.get(url)
    html_content = response.text
    
    # 使用lxml解析HTML
    tree = html.fromstring(html_content)
    
    concept = ''
    
    industry = ''

    xpath_str = f'//*[@id="tw-stock-tabs"]/section[1]/div[2]/a'
    elements = tree.xpath(xpath_str)
    for element in elements:
        industry = industry + f'`{element.text}` ' 
    
    for n in range(1, 10):  # 設定你想要的範圍
        xpath_str = f'//*[@id="tw-stock-tabs"]/section[1]/div[2]/div/span[{n}]'
        elements = tree.xpath(xpath_str)
        for element in elements:
    
            concept = concept + f'`{element.text}` '

    return industry, concept