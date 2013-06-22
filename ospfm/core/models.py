#    Copyright 2012-2013 Sebastien Maccagnoni-Munch
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

from sqlalchemy.schema import UniqueConstraint

from ospfm import db



class Currency(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    owner_username = db.Column(db.String(50),
                               db.ForeignKey('user.username', use_alter=True,
                                             onupdate='CASCADE',
                                             ondelete='CASCADE',
                                             name='fk_owner'))
    isocode        = db.Column(db.String(5), nullable=False)
    symbol         = db.Column(db.String(5), nullable=False)
    name           = db.Column(db.String(50), nullable=False)
    rate           = db.Column(db.Numeric(16, 4))

    def __unicode__(self):
        return u'Currency name "{0}", isocode "{1}", symbol "{2}", rate "{3}"'.format(
                        self.name, self.isocode, self.symbol, self.rate
                    )

    def as_dict(self):
        info = {
            'isocode': self.isocode,
            'symbol': self.symbol,
            'name': self.name
        }
        if self.owner_username:
            info['owner'] = self.owner_username
        if self.rate is not None:
            info['rate'] = self.rate
        return info



class User(db.Model):
    username              = db.Column(db.String(50), nullable=False,
                                      unique=True, primary_key=True)
    first_name            = db.Column(db.String(50), default='',nullable=False)
    last_name             = db.Column(db.String(50), default='',nullable=False)
    passhash              = db.Column(db.String(120), nullable=False)
    preferred_currency_id = db.Column(db.ForeignKey('currency.id'),
                                      nullable=False)

    preferred_currency = db.relationship(
                          'Currency',
                          primaryjoin='User.preferred_currency_id==Currency.id'
                         )

    def __unicode__(self):
        return u'Username "{0}", first name "{1}", last name "{2}"'.format(
                    self.username, self.first_name, self.last_name
                )

    def as_dict(self, own=False):
        info = {
                'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name
        }
        if own:
            info['preferred_currency'] = self.preferred_currency.isocode
            info['emails'] = []
            for email in self.emails:
                info['emails'].append(email.as_dict())
        return info



class UserContact(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    user_username    = db.Column(db.ForeignKey('user.username',
                                               onupdate='CASCADE',
                                               ondelete='CASCADE'),
                                 nullable=False)
    contact_username = db.Column(db.ForeignKey('user.username',
                                               onupdate='CASCADE',
                                               ondelete='CASCADE'),
                                 nullable=False)
    comment          = db.Column(db.String(100), default='', nullable=False)

    __table_args__ = (
        UniqueConstraint('user_username', 'contact_username',
                         name='_user_contact_uc'),
    )

    contact = db.relationship(
                    'User',
                    primaryjoin='UserContact.contact_username==User.username'
                )

    def as_dict(self):
        return {
            'username': self.contact.username,
            'first_name': self.contact.first_name,
            'last_name': self.contact.last_name,
            'comment': self.comment
        }



class UserEmail(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.ForeignKey('user.username',
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'),
                              nullable=False)
    email_address = db.Column(db.String(256), nullable=False)
    # Notification is to be used by (an)other process(es), OSPFM itself doesn't
    # send notifications. This field make it possible to know which email
    # addresses should be used by this/these other process(es).
    notification  = db.Column(db.Boolean, default=False)
    confirmation  = db.Column(db.String(16), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_username', 'email_address',
                         name='_user_address_uc'),
    )

    user = db.relationship('User', backref=db.backref('emails'))

    def as_dict(self):
        return {
            'address': self.email_address,
            'notification': self.notification,
            'confirmed': self.confirmation == 'OK'
        }



class UserPreference(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.ForeignKey('user.username',
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'),
                              nullable=False)
    name          = db.Column(db.String(200), nullable=False)
    value         = db.Column(db.String(2048))

    __table_args__ = (
        UniqueConstraint('user_username', 'name', name='_user_preference_uc'),
    )

    def __unicode__(self):
        return 'For user {0}, {1} = {2}'.format(
                    self.user_username, self.name, self.value
                )

    def as_dict(self):
        return {
            'name': self.name,
            'value': self.value
        }
