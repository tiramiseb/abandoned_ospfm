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

import json

from flask import abort, jsonify
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from ospfm.core import exchangerate, models
from ospfm.database import session
from ospfm.objects import Object

class User(Object):

    def list(self):
        # Users cannot be listed with the API
        self.forbidden()

    def create(self):
        # A user cannot be created with the API
        self.forbidden()

    def read(self, username):
        if username == self.username:
            # When requesting his own information, a user gets more details
            user = models.User.query.options(
                joinedload(models.User.contacts),
                joinedload(models.User.emails),
                joinedload(models.User.preferred_currency)
            ).filter(
                models.User.username == username
            ).one()
            return user.as_dict(own=True)
        else:
            user = models.User.query.filter(
                models.User.username == username
            ).first()
            if not user:
                self.notfound()
            return user.as_dict()

    def update(self, username):
        if username == self.username:
            user = models.User.query.options(
                joinedload(models.User.emails)
            ).filter(
                models.User.username == username
            ).one()
            # A user can only modify his own information
            if self.args.has_key('first_name'):
                user.first_name = self.args['first_name']
            if self.args.has_key('last_name'):
                user.last_name = self.args['last_name']
            if self.args.has_key('preferred_currency'):
                currency = models.Currency.query.filter(
                  and_(
                     models.Currency.isocode == self.args['preferred_currency'],
                     models.Currency.owner == None,
                  )
                ).first()
                if currency:
                    # When preferred currency is changed, all owner's
                    # currencies rates must be changed
                    # XXX Debts amounts should also be changed... when debts will be implemented
                    multiplier = user.preferred_currency
                    multiplier = exchangerate.getrate(
                        user.preferred_currency.isocode,
                        currency.isocode
                    )
                    for c in models.Currency.query.filter(
                        models.Currency.owner_username == username
                    ):
                        c.rate = c.rate * multiplier
                    user.preferred_currency = currency
            if self.args.has_key('emails'):
                emails = json.loads(self.args['emails'])
                if type(emails) == type({}):
                    if emails.has_key('add') and \
                       type(emails['add']) == type([]):
                        for mail in emails['add']:
                            if address not in previous_emails:
                                session.add(
                                    models.UserEmail(
                                        user_username=self.username,
                                        email_address=address
                                    )
                                )
                    if emails.has_key('remove') and \
                       type(emails['remove']) == type([]):
                        for mail in emails['remove']:
                            if address in previous_emails:
                                session.delete(
                                    models.UserEmail.query.filter(
                                        and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                        )
                                    ).first()
                                )
            session.commit()
            return self.read(username)
        else:
            self.forbidden()

    def delete(self, username):
        # A user cannot be deleted with the API
        self.forbidden()

    def __search(self, substring):
        """Search on parts of the users name or on exact email address"""
        if '@' in substring:
            corresponding_rows = models.User.query.join(
                                    models.UserEmail
                          ).filter(models.UserEmail.email_address == substring)
        else:
            substring='%{}%'.format(substring)
            corresponding_rows = models.User.query.filter(
                and_(
                    models.User.username != self.username,
                    or_(
                        models.User.username.like(substring),
                        models.User.first_name.like(substring),
                        models.User.last_name.like(substring),
                    )
                )
            )

        return [u.as_dict() for u in corresponding_rows.all()]

    def http_search(self, substring):
        """
        Search on parts of the users name or on exact email address, from HTTP
        """
        self._Object__init_http()
        return jsonify(status=200, response=self.__search(substring))


class UserContact(Object):

    def list(self):
        contacts = models.UserContact.query.options(
                        joinedload(models.UserContact.contact)
        ).filter(
                        models.UserContact.user_username==self.username
        )
        return [c.contact.as_dict() for c in contacts.all()]

    def create(self):
        contactuser = models.User.query.filter(
                        models.User.username == self.args['username']
                      ).first()
        if not contactuser:
            # XXX If contactuser does not exist, maybe invite him
            self.notfound()
        testcontact = models.UserContact.query.filter(
                        and_(
                            models.UserContact.user_username == self.username,
                   models.UserContact.contact_username == self.args['username']
                        )
                      ).first()
        if testcontact:
            self.badrequest()
        contact = models.UserContact(
                    user_username=self.username,
                    contact=contactuser
                  )
        session.add(contact)
        session.commit()
        return contactuser.as_dict()

    def read(self, username):
        # There is no need to "read" a contact, it is only a "link" to a user
        self.badrequest()

    def update(self, username):
        # A contact may not be updated, only created or deleted
        self.badrequest()

    def delete(self, username):
        contact = models.UserContact.query.filter(
                    and_(
                        models.UserContact.user_username == self.username,
                        models.UserContact.contact_username == username
                    )
        ).first()
        if not contact:
            self.notfound()
        session.delete(contact)
        session.commit()
