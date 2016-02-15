from __future__ import unicode_literals

from time import sleep
from urlparse import urljoin

from selenium.common.exceptions import WebDriverException

from qautobots.framework.helpers import get_application_settings
from qautobots.framework.qanfig import get_config

if get_config()['selenium']['remote']:
    from qautobots.framework.driver import CustomDriver
else:
    from selenium.webdriver import Firefox as CustomDriver


CONFIG = {
    'backend_data_indexing_time': 1.5,
    'page_load_time': 10,
    'sleep_interval': 1,
}


class Browser(CustomDriver):

    def _record_ajax_post(self):
        """Record every AJAX post and store in global JS varaible post_urls"""
        self.execute_script(
            """
            window.post_urls = window.post_urls || [];
            $.ajaxPrefilter(function(options) {
                if(options.type === "POST") {
                    window.post_urls.push(options.url);
                }
            });
            return;
            """
        )

    def _record_ajax_complete(self):
        """Store completed AJAX in global JS variable ajax_complete"""
        self.execute_script(
            """
            window.ajax_complete = window.ajax_complete || [];
            $(document).ajaxComplete(
              function(event, jqxhr, settings, exception) {
                window.ajax_complete.push(settings.url);
            });
            return;
            """
        )

    def navigate(self, url):
        """Navigate to url without authentication."""

        sleep(CONFIG['backend_data_indexing_time'])

        config = get_application_settings()
        base_url = '{protocol}://{host}'.format(**config)
        new_url = urljoin(base_url, url)
        env_url = urljoin(new_url, config['env'])
        self.go_to_url(env_url)

    def navigate_with_auth(self, url, login, password):
        """Navigate to url with authentication"""
        sleep(CONFIG['backend_data_indexing_time'])

        config = get_application_settings()
        config['login'] = login
        config['password'] = password
        base_url = '{protocol}://{login}:{password}@{host}'.format(**config)
        new_url = urljoin(base_url, url)
        self.go_to_url(new_url)

    def go_to_url(self, url):
        """Go to a given URL"""
        if self.current_url != url:
            self.get(url)

        self.maximize_window()
        try:
            self._record_ajax_post()
            self._record_ajax_complete()
        except WebDriverException:
            sleep(2)
