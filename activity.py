# Copyright (C) 2007, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gettext import gettext as _

import os
import sys
import server

OLD_TOOLBAR = False
try:
    from sugar.graphics.toolbarbox import ToolbarBox, ToolbarButton
except ImportError:
    OLD_TOOLBAR = True

#from sugar.activity import registry
#activity_info = registry.get_registry().get_activity('org.laptop.WebActivity')

#sys.path.append(activity_info.path)
if os.path.exists('../Browse.activity'):
    sys.path.append('../Browse.activity')
elif os.path.exists('/usr/share/sugar/activities/Browse.activity'):
    sys.path.append('/usr/share/sugar/activities/Browse.activity')
else:
    print 'This activity need a Browser activity installed to run'

import webactivity

from searchtoolbar import SearchToolbar

# Default settings.
WIKIDB = 'es_PE/es_PE.xml.bz2'
HOME_PAGE = '/static/'

# Activity class, extends WebActivity.
class WikipediaActivity(webactivity.WebActivity):
    def __init__(self, handle):
        
        print "Starting server...\n"
        
        os.chdir(os.environ['SUGAR_BUNDLE_PATH'])

        self.HTTP_PORT = '8000'
        server.load_db(WIKIDB)
        server.run_server({ 'path': WIKIDB,
                            'port': int(self.HTTP_PORT) })

        handle.uri = 'http://localhost:%s%s' % (self.HTTP_PORT, HOME_PAGE)

        webactivity.WebActivity.__init__(self, handle)

        # Use xpcom to set a RAM cache limit.  (Trac #7081.)
        from xpcom import components
        from xpcom.components import interfaces
        cls = components.classes['@mozilla.org/preferences-service;1']
        pref_service = cls.getService(interfaces.nsIPrefService)
        branch = pref_service.getBranch("browser.cache.memory.")
        branch.setIntPref("capacity", "5000")

        # Use xpcom to turn off "offline mode" detection, which disables
        # access to localhost for no good reason.  (Trac #6250.)
        ios_class = components.classes["@mozilla.org/network/io-service;1"]
        io_service = ios_class.getService(interfaces.nsIIOService2)
        io_service.manageOfflineStatus = False

        self.searchtoolbar = SearchToolbar(self)
        # WTB: Hacked to use hardcoded Spanish localization for WikiBrowse release.
        if OLD_TOOLBAR:
            self.toolbox.add_toolbar('Buscar', self.searchtoolbar)
        else:
            search_toolbar_button = ToolbarButton()
            search_toolbar_button.set_page(self.searchtoolbar)
            search_toolbar_button.props.icon_name = 'search'
            search_toolbar_button.props.label = _('Search')
            self.get_toolbar_box().toolbar.insert(search_toolbar_button, 1)
            search_toolbar_button.show()

        self.searchtoolbar.show()

    def _get_browser(self):
        if hasattr(self, '_browser') and callable(self._browser):
            # Browse < 109
            return self._browser
        else:
            return self._tabbed_view.props.current_browser

    def _load_homepage(self):
        home_url = 'http://localhost:%s%s' % (self.HTTP_PORT, HOME_PAGE)
        browser = self._get_browser()
        browser.load_uri(home_url)
