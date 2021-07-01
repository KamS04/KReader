from requests import Session
import requests

class CannotBypassCloudflare(Exception):
    def __init__(self):
        super(CannotBypassCloudflare, self).__init__('Could not bypass cloudflare')


class CloudFlareInterceptor(Session):
    def __init__(self, domain):
        #TODO get saved session cookies and stuff
        self.domain = domain

    def request(self, method, url, **kwargs):
        request = super(CloudFlareInterceptor, self).request(method, url, **kwargs)

        if request.status_code == 503 and b'cloudflare' in request.content:
            raise CannotBypassCloudflare()
        
        return request

    def bypassed_cloudflare(self, driver):
        cookies = driver.get_cookies()
        self.headers['User-Agent'] = driver.execute_script('return navigator.UserAgent')
        for cookie in cookies:
            self.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        self.update()
    
    def update(self):
        #TODO Save session data
        pass