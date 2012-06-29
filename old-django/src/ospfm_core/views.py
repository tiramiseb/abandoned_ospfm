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

from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView, View

from ospfm_core import forms, models

class ProfileView(UpdateView):
    model = models.UserProfile
    form_class = forms.ProfileForm
    template_name = 'ospfm_core/profile.html'
    success_url = reverse_lazy('core-profile')

    def get_object(self):
        return models.UserProfile.objects.get(user=self.request.user)


class ContactsView(View):
    pass

class CurrenciesView(View):
    pass
