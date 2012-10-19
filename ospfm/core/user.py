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
import os

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
                previous_emails = []
                previous_notifications = []
                for address in models.UserEmail.query.filter(
                              models.UserEmail.user_username == self.username):
                    previous_emails.append(address.email_address)
                    if address.notification:
                        previous_notifications.append(address.email_address)
                print previous_emails
                print previous_notifications
                if type(emails) == type({}):
                    if emails.has_key('add') and \
                       type(emails['add']) == type([]):
                        for address in emails['add']:
                            if address not in previous_emails:
                                # Use random hash for email confirmation
                                # Email confirmation is done outside of OSPFM
                                # Another process must read the database and
                                # send confirmation emails
                                randomhash = os.urandom(8).encode('hex')
                                session.add(
                                    models.UserEmail(
                                        user_username=self.username,
                                        email_address=address,
                                        confirmation=randomhash
                                    )
                                )
                    if emails.has_key('remove') and \
                       type(emails['remove']) == type([]):
                        for address in emails['remove']:
                            if address in previous_emails:
                                session.delete(
                                    models.UserEmail.query.filter(
                                        and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                        )
                                    ).first()
                                )
                    if emails.has_key('enablenotifications') and \
                       type(emails['enablenotifications']) == type([]):
                        for address in emails['enablenotifications']:
                            if address not in previous_notifications:
                                models.UserEmail.query.filter(
                                    and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                    )
                                ).first().notification = True
                    if emails.has_key('disablenotifications') and \
                       type(emails['disablenotifications']) == type([]):
                        for address in emails['disablenotifications']:
                            if address in previous_notifications:
                                models.UserEmail.query.filter(
                                    and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                    )
                                ).first().notification = False


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
            ).filter(
                models.UserEmail.email_address == substring,
                models.UserEmail.confirmation == 'OK'
            )
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

    emptyvalid = ['comment']

    def list(self):
        contacts = models.UserContact.query.options(
                        joinedload(models.UserContact.contact)
        ).filter(
                        models.UserContact.user_username==self.username
        )
        return [c.as_dict() for c in contacts.all()]

    def create(self):
        if not self.args.has_key('username'):
            self.badrequest()
        # Verify the contact exists
        contactuser = models.User.query.filter(
                        models.User.username == self.args['username']
                      ).first()
        if not contactuser:
            # XXX If contactuser does not exist, maybe invite him
            self.notfound()
        # Verify the user doesn't already have this contact
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
                    contact=contactuser,
                    comment=self.args.get('comment', '')
                  )
        session.add(contact)
        session.commit()
        return contact.as_dict()

    def read(self, username):
        contact = models.UserContact.query.filter(
            and_(
                models.UserContact.user_username == self.username,
                models.UserContact.contact_username == self.args['username']
            )
        ).first()
        if not contact:
            self.notfound()
        return contact.as_dict()

    def update(self, username):
        contact = models.UserContact.query.filter(
            and_(
                models.UserContact.user_username == self.username,
                models.UserContact.contact_username == self.args['username']
            )
        ).first()
        if not contact:
            self.notfound()
        # Only the comment can be updated
        if self.args.has_key('comment'):
            contact.comment = self.args['comment']
            session.commit()
        return contact.as_dict()

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
