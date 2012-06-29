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

from django.forms import ModelForm, ModelChoiceField

from ospfm_core import models

class CurrencyForm(ModelForm):
    class Meta:
        model = models.Currency

class ProfileForm(ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['preferred_currency'] = ModelChoiceField(
                                    models.Currency.objects.filter(owner=None),
                                    empty_label=None
                                            )

class ContactForm(ModelForm):
    class Meta:
        model = models.UserContact
