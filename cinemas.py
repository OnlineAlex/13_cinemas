import requests
import collections as cl
import datetime
from bs4 import BeautifulSoup


PROXY = 'https://192.116.142.153:8080'


def fetch_afisha_page_data(day, page):
    afisha_page = 'https://www.afisha.ru/msk/schedule_cinema/'
    search_params = {
        'date': day,
        'afishachoice': 'false',
        'kids': 'false',
        'sort': 'popular',
        'view': 'cards',
        'page': page
    }
    try:
        response = requests.get(
            afisha_page,
            params=search_params,
            headers={'Accept': 'application/json'}
        )
    except requests.ConnectionError:
        return None
    response.encoding = 'utf8'
    return response.json()


def get_proxies_list():
    params = {
        'anonymity': 'false',
        'count': 100,
        'country': 'RU%2C+UA%2C+BY%2C+KZ',
        'token': 'demo'
    }
    response = requests.get('http://www.freeproxy-list.ru/api/proxy', params=params)
    return response.content.decode('utf8').splitlines()


def parse_afisha_list(movie_list):
    afisha_list = []
    for movie in movie_list:
        afisha_list.append(movie['Name'])
    return afisha_list


def fetch_movie_rating(movie):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    searching_response = requests.get(
        'https://www.kinopoisk.ru/',
        params={'kp_query': movie.replace(' ', '%20')},
        headers=headers,
        proxies={'https': PROXY}
    )
    search_page = BeautifulSoup(searching_response.text, 'html.parser')
    try:
        rating = search_page.find(
            'div', {'class': 'most_wanted'}
        ).findChild(
            'div', {'class': 'rating'}
        ).text
        return round(float(rating), 1)
    except (AttributeError, TypeError):
        return 0


def output_movies_to_console(movies):
    for movie, rating in movies:
        print('{:>40} — {}'.format(movie, rating))


if __name__ == '__main__':
    print('\nИщу фильмы в прокате')
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    page_data = fetch_afisha_page_data(today, page=1)
    if page_data is None:
        exit('Нет соеденения. Проверь интернет.')
    movies_title = parse_afisha_list(page_data['MovieList']['Items'])
    pages_count = page_data['Pager']['PagesCount']+1
    for page_num in range(2, pages_count):
        page_data = fetch_afisha_page_data(today, page_num)
        movies_title += parse_afisha_list(page_data['MovieList']['Items'])
    print('Фильмов найдено — {}\nПроверяю рейтинги\n'.format(len(movies_title)))
    movies_rating = cl.Counter()
    for movie_title in movies_title:
        movies_rating[movie_title] = fetch_movie_rating(movie_title)
        print(len(movies_rating))

    number_movies = 10
    output_movies_to_console(movies_rating.most_common(number_movies))
