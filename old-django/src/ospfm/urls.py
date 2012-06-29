#    Copyright 2012 Sebastien Maccagnoni-Munch
#
#    This file is part of OSPFM.
#
#    OSPFM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OSPFM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with OSPFM.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView

from ospfm_core import urls as core_urls

admin.autodiscover()

urlpatterns = patterns('',
    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # Login and stuff
    url(r'^accounts/login/', 'django.contrib.auth.views.login',
        {'template_name':'login.html'}, name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout_then_login',
        name='logout'),
    url('^accounts/$', RedirectView.as_view(url='/')),
    url('^accounts/profile/$', RedirectView.as_view(url='/')),

    # Home
    url(r'^$', login_required(TemplateView.as_view(template_name="index.html")), name='home'),

    # OSPFM apps
    url(r'^ospfm_core/', include(core_urls)),
)
