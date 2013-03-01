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

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from ospfm.database import Base


class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    owner_username = Column(String(50), ForeignKey('user.username',
                            use_alter=True, name='fk_owner'))
    isocode = Column(String(5), nullable=False)
    symbol = Column(String(5), nullable=False)
    name = Column(String(50), nullable=False)
    rate = Column(Numeric(16, 4))

    owner = relationship('User',
                         primaryjoin='Currency.owner_username==User.username')

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

class User(Base):
    __tablename__ = 'user'
    username = Column(String(50), nullable=False, unique=True,
                      primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    passhash = Column(String(60), nullable=False)
    preferred_currency_id = Column(ForeignKey('currency.id'), nullable=False)

    preferred_currency = relationship(
                          'Currency',
                          primaryjoin='User.preferred_currency_id==Currency.id'
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


class UserContact(Base):
    __tablename__ = 'usercontact'
    id = Column(Integer, primary_key=True)
    user_username = Column(ForeignKey('user.username'), nullable=False)
    contact_username = Column(ForeignKey('user.username'), nullable=False)
    comment = Column(String(100), default='', nullable=False)

    __table_args__ = (
        UniqueConstraint('user_username', 'contact_username',
                         name='_user_contact_uc'),
    {})

    user = relationship(
                'User',
                primaryjoin='UserContact.user_username==User.username'
           )

    contact = relationship(
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


class UserEmail(Base):
    __tablename__ = 'useremail'
    id = Column(Integer, primary_key=True)
    user_username = Column(ForeignKey('user.username'), nullable=False)
    email_address = Column(String(256), nullable=False)
    # Notification is to be used by (an)other process(es), OSPFM itself doesn't
    # send notifications. This field make it possible to know which email
    # addresses should be used by this/these other process(es).
    notification = Column(Boolean(), default=False)
    confirmation = Column(String(16), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_username', 'email_address',
                         name='_user_address_uc'),
    {})

    user = relationship('User', backref='emails')

    def as_dict(self):
        return {
            'address': self.email_address,
            'notification': self.notification,
            'confirmed': self.confirmation == 'OK'
        }


class UserPreference(Base):
    __tablename__ = 'userpreference'
    id = Column(Integer, primary_key=True)
    user_username = Column(ForeignKey('user.username'), nullable=False)
    name = Column(String(200), nullable=False)
    value = Column(String(2048))

    __table_args__ = (
        UniqueConstraint('user_username', 'name',
                         name='_user_preference_uc'),
    {})

    def as_dict(self):
        return {
            'name': self.name,
            'value': self.value
        }
