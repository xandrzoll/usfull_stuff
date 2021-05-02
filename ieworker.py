import time
from win32com.client import Dispatch


class IEWorker:
    use_auth = True
    auth_url = ''
    auth_login_id = ''
    auth_pwd_id = ''
    auth_login = ''
    auth_pwd = ''
    auth_button = ''
    auth_title_page = ''
    set_delay = 0.5

    def __init__(self, url='', use_auth=True):
        if url:
            win_id = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
            win_shells = Dispatch(win_id)
            url = url.lower()
            for win_shell in win_shells:
                if url in win_shell.LocationURL.lower():
                    self.ie = win_shell
                    return
        self.ie = Dispatch("InternetExplorer.Application")
        self.ie.Visible = True
        if url:
            self.navigate(url)

    def _navigate(self, url):
        self.ie.Navigate(url)
        self.ie_busy()
        time.sleep(self.set_delay)
        self._get_DOM()

    def navigate(self, url):
        self._navigate(url)
        if self.check_auth():
            self.auth()
            self.ie_busy()
            if url != self.auth_url and url != self.ie.LocationURL:
                self._navigate(url)

    def ie_busy(self):
        while self.ie.Busy:
            time.sleep(0.1)

    def close(self):
        self.ie.Quit()
        self.ie = None

    def _get_DOM(self):
        self._DOM = []
        elems = self.ie.Document.all
        for elem in elems:
            self._DOM.append({
                'elem': elem,
                'tag': elem.tagName,
                'id': elem.getAttribute('id'),
                'name': elem.getAttribute('name'),
            })

    def get_elements(self, id='', name='', cls='', tag='', reload_DOM=False):
        if reload_DOM:
            self._get_DOM()

        elems = self._DOM
        elems = list(filter(lambda x: x['tag'] == tag.upper() if tag else x, elems))
        elems = list(filter(lambda x: x['name'] == name if name else x, elems))
        elems = list(filter(lambda x: x['id'] == id if id else x, elems))

        if len(elems) == 1:
            elems = elems[0]
        elif len(elems) == 0:
            elems = None

        return elems

    def find_button_by_name(self, name='', tag='BUTTON', reload_DOM=False):
        if reload_DOM:
            self._get_DOM()

        elems = self._DOM
        elems = list(filter(lambda x: x['tag'] == tag.upper() if tag else x, elems))
        buttons = []
        for elem in  elems:
            if elem['elem'].outerText == name:
                buttons.append(elem['elem'])

        return buttons

    def set_auth(self,
                 auth_url='',
                 auth_login_id='',
                 auth_pwd_id='',
                 auth_login='',
                 auth_pwd='',
                 auth_button='',
                 auth_title_page=''
                 ):
        self.use_auth = True
        self.auth_url = auth_url
        self.auth_login_id = auth_login_id
        self.auth_pwd_id = auth_pwd_id
        self.auth_login = auth_login
        self.auth_pwd = auth_pwd
        self.auth_button = auth_button
        self.auth_title_page = auth_title_page

    def check_auth(self):
        if self.ie.LocationURL == self.auth_url:
            return True
        elif self.ie.Document.Title == self.auth_title_page:
            return True
        else:
            return False

    def auth(self):
        login = self.get_elements(id=self.auth_login_id)['elem']
        pwd = self.get_elements(id=self.auth_pwd_id)['elem']
        button = self.get_elements(id=self.auth_button)['elem']
        login.setAttribute('value', self.auth_login)
        time.sleep(self.set_delay)
        pwd.setAttribute('value', self.auth_pwd)
        time.sleep(self.set_delay)
        button.click()

    def frame(self, num):
        return IEFrame(self.ie.Document.frames[num])


class IEFrame(IEWorker):
    def __init__(self, frame):
        self.ie = frame
        self._get_DOM()


if __name__ == '__main__':
    ie = IEWorker()

    ie.navigate(
        'google.ru')

    frame = ie.frame(0)

    combobox = ie.ie.get_elements(id='X6', tag='INPUT')
