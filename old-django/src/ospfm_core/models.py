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

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from ospfm import settings
from ospfm_core import exchangerate


class Currency(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True,
                            help_text="used only for user-defined currencies")
    symbol = models.CharField(
                max_length=5,
                help_text=("for standard currencies, "
                           "three-letter ISO-4217 language code"))
    rate = models.DecimalField(
                max_digits=13, decimal_places=4, null=True, blank=True,
                help_text=('used only for user-defined currencies. conversion '
                           'rate from the preferred currency to this one.'))

    def get_rate(self, target_currency):
        """
        Return the exchange rate from this currency to the target currency

        """
        # Both currencies are global
        if (not self.rate) and (not target_currency.rate):
            return exchangerate.getrate(self.symbol, target_currency.symbol)
        # Both currencies are user-defined
        elif self.rate and target_currency.rate:
            return target_currency.rate / self.rate
        # Only source currency is user-defined
        elif self.rate and (not target_currency.rate):
            profile_currency = self.owner.get_profile().preferred_currency
            target_rate = exchangerate.getrate(profile_currency.symbol,
                                               target_currency.symbol)
            return target_rate / self.rate
        # Only target currency is user-defined
        elif (not self.rate) and target_currency.rate:
            profile_currency = target_currency.owner.get_profile().preferred_currency
            self_rate = exchangerate.getrate(profile_currency.symbol,
                                             self.symbol)
            return target_currency.rate / self_rate

    def clean(self):
        if self.owner and not self.name:
            raise ValidationError('A user-defined currency should have a name')
        if self.owner and not self.rate:
            raise ValidationError('A user-defined currency should have a rate')
        if (not self.owner) and self.name:
            raise ValidationError(
                'A global currency\'s name should be defined in language files'
            )
        if (not self.owner) and self.rate:
            raise ValidationError('A global currency shouldn\'t have a rate')

    def __unicode__(self):
        if self.name:
            name = self.name
        else:
            currencyname = '%s currency name' % self.symbol
            name = _(currencyname)
        return '%(symbol)s: %(name)s' % {'symbol':self.symbol, 'name':name}

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')
        ordering = ['symbol']
        unique_together = ('owner', 'symbol')


def get_euro():
    try:
        euro = Currency.objects.get(symbol='EUR')
    except:
        # If the "EUR" currency is not defined, there will be no default
        # currency automatically assigned to a new user
        euro = None
    return euro
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    preferred_currency = models.ForeignKey(Currency, null=True,
                                           default=get_euro)

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_preferred_currency = self.preferred_currency

    def clean(self):
        if self.preferred_currency and self.preferred_currency.owner:
            raise ValidationError(
                'A user-defined currency cannot be set as preferred currency'
            )

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        # Change user-defined currencies' rates
        if self.__original_preferred_currency:
            # Do not do that if there is no original preferred currency
            # (when the user sets his preferred currency for the first time)
            multiplier = self.__original_preferred_currency.get_rate(
                            self.preferred_currency
                         )
            for currency in Currency.objects.filter(owner=self.user):
                currency.rate = currency.rate * multiplier
                currency.full_clean()
                currency.save()
        self.__original_preferred_currency = self.preferred_currency

    def __unicode__(self):
        return _("%s's profile") % self.user

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('users profiles')


class UserContact(models.Model):
    user = models.ForeignKey(User)
    contact = models.ForeignKey(User, related_name='+')

    def clean(self):
        if self.user == self.contact:
            raise ValidationError('User cannot be in his own contact list.')

    def __unicode__(self):
        return _("%(contact)s is one of %(user)s's contacts") % {
                    'user':self.user,
                    'contact':self.contact
                }

    class Meta:
        verbose_name = _('user contact')
        verbose_name_plural = _('users contacts')
        unique_together = ('user', 'contact')


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
models.signals.post_save.connect(create_user_profile, sender=User)
