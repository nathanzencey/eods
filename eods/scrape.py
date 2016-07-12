import bs4
import numpy as np
import pandas as pd
import re
import urllib2


class Place(object):

    def __init__(self, input_dict):

        self.loc = input_dict['Location']
        self.state = input_dict['State']
        self.pop = input_dict['Population (US Census, 2011)']
        self.ownership = input_dict['Ownership?']
        self.policy = input_dict['Open Data Policy?']
        self.link = input_dict['Link']
        self.type = input_dict['Type']

        self.datasets = None

        self._get_info()

    @property
    def shortlink(self):

        return self.link.lstrip('htps').lstrip(':/').rstrip('/')

    @property
    def name(self):

        return '{0} ({1})'.format(self.loc, self.shortlink)

    @property
    def _link_to_try(self):

        link = (self.link if self.link[-1] == '/' else self.link + '/')

        return link + 'browse?sortBy=most_accessed'

    def _get_info(self):

        # TODO: fix case where URL works but returns a 404 page instead of error
        try:
            s = self._get_soup(self._link_to_try)
        except urllib2.HTTPError:
            pass
        else:
            print('Starting: ' + self.name)
            self.datasets = pd.DataFrame()
            for res in self._read_page(s):
                self._parse_result(res)
            end_page_num = self._get_end_num(s)
            if end_page_num:
                self._read_all_pages(2, end_page_num + 1)
            v = self.datasets['views']
            self.datasets['views_norm'] = v / np.linalg.norm(v, ord=np.inf)
            print('Completed: ' + self.name)
        finally:
            return

    def _read_all_pages(self, start, end):

        #for num in range(start, end):
        for num in range(start, 4):
            url = self._link_to_try + '&utf8=%E2%9C%93&page=' + str(num)
            for result in self._read_page(self._get_soup(url)):
                self._parse_result(result)
            if num % 10 == 0: print('Completed page ' + str(num))

        return

    @staticmethod
    def _get_soup(url):

        return bs4.BeautifulSoup(urllib2.urlopen(url).read(), 'html.parser')

    @staticmethod
    def _read_page(page_soup):

        return page_soup.find_all('div', {'class': 'browse2-result'})

    def _parse_result(self, result):

        def _find(child_tag_type, class_):

            child_tag = result.find(child_tag_type,
                                    {'class': 'browse2-result-' + class_})
            if child_tag == None:
                return None
            else:
                return child_tag.text.strip().encode('utf-8')

        # TODO: handles cases where the title background is gray
        result_dict = {
            'name': _find('a', 'name-link'),
            'category': _find('a', 'category'),
            'type': _find('span', 'type-name'),
            'topics': [t.text.strip() for t in
                result.find_all('a', {'class': 'browse2-result-topic'})],
            'views': self._integer(_find('div', 'view-count-value')),
            'descrip': _find('div', 'description')
        }

        self.datasets = self.datasets.append(result_dict, ignore_index=True)

        return

    @staticmethod
    def _get_end_num(page_soup):

        link = page_soup.find('a', {'class': 'lastLink'}).get('href')
        end_num = re.search(r".+&page=(\d+)", link).group(1)

        return int(end_num)

    @staticmethod
    def _integer(number_string):

        return int(number_string.replace(',', ''))

    def make_csv(self, folder='output/'):

        file_name = re.sub(r"[\.\[\] (]", r"_", self.name).replace(')', '.csv')
        if self.datasets is not None:
            self.datasets.to_csv(folder + file_name, index=False)
            print('Exported file: ' + file_name)

        return


def visit_all_sites(file_path='data/local_open_data_portals.csv'):

    print('Scraping all Socrata sites. This may take a few minutes.\n')
    all_places_df = pd.read_csv(file_path)
    all_places = {}
    for row in all_places_df.iterrows():
        new_place = Place(row[1].to_dict())
        all_places[new_place.name] = new_place
    socrata_places = {k: v for k, v in all_places.iteritems()
        if (v.datasets is not None) and not v.datasets.empty}

    return all_places, socrata_places

def make_csvs(dict_, folder='output/'):

    for place in dict_.values():
        place.make_csv(folder)

    return


if __name__ == '__main__':

    all_places, socrata_places = visit_all_sites()
    make_csvs(socrata_places)
