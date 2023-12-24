import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import csv
import lxml
import time
from datetime import datetime

data_list = []

async def get_page_data(session, i):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    url = f"https://www.labirint.ru/genres/2308/?available=1&preorder=1&paperbooks=1&otherbooks=1&page={i}"

    async with session.get(url = url,headers = headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')
        # cписок в котором находятся все данные
        all_products_list = soup.find_all('div', class_ = 'products-row')[1].find_all('div', class_ = 'card-column card-column_gutter col-xs-6 col-sm-3 col-md-1-5 col-xl-2')
        # добыча информации из списка 
        for item in all_products_list:
            product_name = item.find('span', class_ = 'product-title').text
            try:
                product_author = item.find('div', class_ = 'product-author').find('span').text
            except Exception:
                product_author = "Информация не найдена"
            product_published_first_path = item.find('a', class_ = 'product-pubhouse__pubhouse').find('span').text
            try:
                product_published_second_path = item.find('a', class_ = 'product-pubhouse__series').find('span').text
            except Exception:
                product_published_second_path = ""
            product_published = product_published_first_path +':' + product_published_second_path
            price_val = item.find('span', class_ = 'price-val').find('span').text
            try:
                price_old = item.find('span', class_ = 'price-gray').text
            except Exception:
                price_old = ''
            try:
                product_discount = item.find('span', class_ = 'card-label__text card-label__text_turned').text
            except Exception:
                product_discount = ''
            data_list.append(
                {
                'product_name': product_name,
                'product_author': product_author,
                'product_published': product_published,
                'price_val': price_val,
                'price_old': price_old,
                'product_discount': product_discount,
                'product_available': 'На складе'

                }
            )
    print(f'ИНФО ОБРАБОТАЛ СТРАНИЦУ {i}')


async def gather_data():
    url = 'https://www.labirint.ru/genres/2308/?available=1&preorder=1&paperbooks=1&otherbooks=1&'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        # Открываем сессию, которая будет использоваться в функции get_page_data(), а также ниже для полученя пагинации сайта
    async with aiohttp.ClientSession() as session:
        # Делаем get запрос и забираем отткуда пагинацию
        response = await session.get(url = url, headers = headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        page_count = int(soup.find('div', class_ ='pagination-numbers__right').find_all('a')[-1].text)

        tasks = []
        # цикл для прохода стрниц сайта и формирования задач
        for i in range(1, page_count + 1):
            task = asyncio.create_task(get_page_data(session, i))
            tasks.append(task)
        # объединяем задачи
        await asyncio.gather(*tasks)

def main():
    asyncio.run(gather_data())

    with open('data.json', 'w', encoding = 'utf-8') as file:
        json.dump(data_list, file, indent = 4, ensure_ascii= False)

    with open('all_data.csv','w', encoding = "cp1251", newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Название книги","Автор книги","Издатель книги","Цена со скидкой","Цена без скидки","Скидка"])

    for data in data_list:
        with open('all_data.csv','a', encoding = "cp1251", newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                data['product_name'],
                data['product_author'],
                data['product_published'],
                data['price_val'],
                data['price_old'],
                data['product_discount']
                )
            )

if __name__ == '__main__':
    main()


