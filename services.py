from functools import partial
import requests


class ITrackService(object):

    __url = None
    __http_get = None
    __search = None
    __parser = None
    __fields = None
    __expand = None

    def __init__(self, url='https://itrack.barco.com', auth=None,
                 fields=None, expand=None, parser=lambda x: x):
        self.__url = url
        self.__http_get = partial(requests.get, auth=auth)
        self.__search = partial(self.__http_get, url + '/rest/api/latest/search')
        self.__fields = fields
        self.__expand = expand
        self.__parser = parser

    def issue(self, url):
        ##print(dict(url=url))
        return self.__http_get(url, params=dict(fields=self.__fields, expand=self.__expand)).json()

    def _search(self, jql, start_at, max_results):
        ##print(dict(jql=jql, start_at=start_at, max_results=max_results))
        params=dict(jql=jql, fields=self.__fields, expand=self.__expand,
                    startAt=start_at, maxResults=max_results)
        return self.__search(params=params).json()

    def search(self, jql, start_at=0, chunk_size=50):
        data = self._search(jql, start_at, chunk_size)
        issues, total = data['issues'], data['total']
        yield from (self.__parser(x) for x in issues)
        count = start_at + len(issues)
        if count >= total: raise StopIteration
        yield from self.search(jql, start_at=count, chunk_size=chunk_size)

    def count(self, jql):
        return int(self._search(jql, 0, 1)['total'])

    def sprints(self, board_id, state='active'):
        url = self.__url + '/rest/agile/1.0/board/{:d}/sprint'.format(board_id)
        print(dict(url=url, params=dict(state=state)))
        data = self.__http_get(url, params=dict(state=state)).json()
        if 'values' in data:
            yield from (x['id'] for x in data['values'])

    def stories(self, sprint_id):
        yield from self.search('Sprint={}'.format(sprint_id))

