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

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from ospfm_core import views

urlpatterns = patterns('ospfm_core.views',

    url(r'^currencies/$', login_required(views.CurrenciesView.as_view()),
                          name='core-currencies'),
    url(r'^profile/$', login_required(views.ProfileView.as_view()),
                       name='core-profile'),
    url(r'^contacts/$', login_required(views.ContactsView.as_view()),
                        name='core-contacts'),
)
