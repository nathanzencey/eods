import bs4
import csv
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

        self.datasets = pd.DataFrame()

        self._get_info()

    @property
    def shortlink(self):

        return self.link.lstrip('htps:/').rstrip('/')

    @property
    def name(self):

        return '{0} ({1})'.format(self.loc, self.shortlink)

    @property
    def _link_to_try(self):

        link = (self.link if self.link[-1] == '/' else self.link + '/')

        return link + 'browse?sortBy=most_accessed'

    def _get_info(self):

        try:
            s = self._get_soup(self._link_to_try)
        except urllib2.HTTPError:
#            self.soup = None
            pass
        else:
            # self.soup = s
            # self._read_page(s)
            # get first page results
            for res in self._read_page(s):
                self._parse_result(res)
            end_page_num = self._get_end_num(s)
            if end_page_num:
                self._read_all_pages(2, end_page_num + 1)
            # if end page number: read all other pages
        finally:
            return

    def _read_all_pages(self, start, end):

        #for num in range(start, end):
        for num in range(start, 4):
            url = self._link_to_try + '&utf8=%E2%9C%93&page=' + str(num)
            for result in self._read_page(self._get_soup(url)):
                self._parse_result(result)

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

            return child_tag.text.strip().encode('utf-8')

        result_dict = {
            'name': _find('a', 'name-link'),
#            'category': _find('a', 'category'),
            'type': _find('span', 'type-name'),
#            'topics': [t.test.strip() for t in
#                result.find_all('a', {'class': 'browse2-result-topic'})],
            'views': self._integer(_find('div', 'view-count-value'))
            #'descrip': _find('div', 'description')
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


def visit_all_sites():

    # for row in CSV, visit_site(row)

    return

def visit_site():

    return


