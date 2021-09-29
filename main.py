from bs4 import BeautifulSoup
import aiohttp
import asyncio
from fake_useragent import UserAgent
import xlsxwriter

cookie = '' # Сюда ваши куки(если требуются)
data = []  # Массив со всеми данными


async def main():
    async with aiohttp.ClientSession() as session:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user_agent': UserAgent()['google_chrome'],
            'cookie': cookie
        }
        async with session.get(url='https://lolz.guru/articles/', headers=headers) as response:
            response_text = await response.text()

        nextpageurl = '?page='
        soup = BeautifulSoup(response_text, 'html.parser')
        pages = int(soup.find('div', class_='PageNav').find_all('a')[-1].get_text())
        tasks = []
        for i in range(1, pages+1):
            tasks.append(parsing_page(session, f'https://lolz.guru/articles/{nextpageurl}{i}'))

        await asyncio.gather(*tasks)
        write_xlsx(data)

async def parsing_page(session, url):
    headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user_agent': UserAgent()['google_chrome'],
            'cookie': cookie
        }
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'html.parser')
        tables = soup.find_all('div', class_='articleItem') # Посик всех статьей на странице
        for table in tables:
            try:
                data.append(
                     {
                         'articename': table.find('a', class_='articleTitleLink').get_text(),
                         'articelink': 'https://lolz.guru/'+table.find('a', class_='articleTitleLink')['href'],
                         'username': table.find('a', class_='username').get_text(),
                         'userlink': 'https://lolz.guru/'+table.find('a', class_='username')['href'],
                         'imglink': 'https://lolz.guru/'+table.find('a', class_='attachHolder')['href']
                     }
                )
            except:
                data.append(
                    {
                        'articename': table.find('a', class_='articleTitleLink').get_text(),
                        'articelink': 'https://lolz.guru/'+table.find('a', class_='articleTitleLink')['href'],
                        'username': table.find('a', class_='username').get_text(),
                        'userlink': None,
                        'imglink': 'https://lolz.guru/'+table.find('a', class_='attachHolder')['href']
                    }
                )


def write_xlsx(data):
    workbook = xlsxwriter.Workbook('./articles_lolzguru.xlsx') # Открытие файла
    worksheet = workbook.add_worksheet() # Созадние листа
    # Заносим заголовки
    worksheet.write('A1', 'Название статьи')
    worksheet.write('B1', 'Ссылка на статью')
    worksheet.write('C1', 'Имя автора')
    worksheet.write('D1', 'Ссылка на автора')
    worksheet.write('E1', 'Ссылка на главное фото статьи')
    a,b,c,d,e = 2,2,2,2,2
    for line in data: # Начинаем заносить данные в таблицу
        worksheet.write(f'A{a}', line['articename'])
        a += 1
        worksheet.write(f'B{b}', line['articelink'])
        b += 1
        worksheet.write(f'C{c}', line['username'])
        c += 1
        worksheet.write(f'D{d}', line['userlink'])
        d += 1
        worksheet.write(f'E{e}', line['imglink'])
        e += 1
    workbook.close() # Сохраняем и завершаем работу с файлом

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
