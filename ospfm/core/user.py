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

import json
import os

from passlib.hash import sha512_crypt

from flask import jsonify

from ospfm import authentication, config, db
from ospfm.core import exchangerate, models
from ospfm.objects import Object

class User(Object):

    def list(self):
        # Users cannot be listed with the API
        self.forbidden("Listing all users is forbidden")

    def create(self):
        # A user cannot be created with the API
        self.forbidden("A user cannot be created with the API")

    def read(self, username):
        if username == 'me' or username == self.username:
            # When requesting his own information, a user gets more details
            user = models.User.query.options(
                db.joinedload(models.User.emails),
                db.joinedload(models.User.preferred_currency)
            ).filter(
                models.User.username == self.username
            ).one()
            return user.as_dict(own=True)
        else:
            user = models.User.query.filter(
                models.User.username == username
            ).first()
            if not user:
                self.notfound('This user does not exist')
            return user.as_dict()

    def update(self, username):
        if username == 'me' or username == self.username:
            # A user can only modify his own information
            user = models.User.query.options(
                db.joinedload(models.User.emails)
            ).filter(
                models.User.username == self.username
            ).one()
            if 'first_name' in self.args:
                user.first_name = self.args['first_name']
            if 'last_name' in self.args:
                user.last_name = self.args['last_name']
            if 'password' in self.args and \
               username not in config.DEMO_ACCOUNTS:
                if 'currentpassword' in self.args and \
                           authentication.authenticate(
                                username,
                                self.args['currentpassword'],
                                False
                           ):
                    if len(self.args['password']) < 8:
                        self.badrequest(
                               'Password should be at least 8 characters long')
                    user.passhash = sha512_crypt.encrypt(
                                        self.args['password'],
                                        rounds=config.PASSWORD_SALT_COMPLEXITY
                                    )
                else:
                    self.badrequest(
                                 "Please provide the correct current password")
            if 'preferred_currency' in self.args:
                currency = models.Currency.query.filter(
                  db.and_(
                     models.Currency.isocode == self.args['preferred_currency'],
                     models.Currency.owner_username == None,
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
                        models.Currency.owner_username == self.username
                    ):
                        c.rate = c.rate * multiplier
                    user.preferred_currency = currency
                    self.add_to_response('totalbalance')
            if 'emails' in self.args:
                emails = json.loads(self.args['emails'])
                previous_emails = []
                previous_notifications = []
                for address in models.UserEmail.query.filter(
                              models.UserEmail.user_username == self.username):
                    previous_emails.append(address.email_address)
                    if address.notification:
                        previous_notifications.append(address.email_address)
                if type(emails) == type({}):
                    if 'add' in emails and \
                       type(emails['add']) == type([]) and \
                       username not in config.DEMO_ACCOUNTS:
                        for address in emails['add']:
                            if address not in previous_emails:
                                # Use random hash for email confirmation
                                # Email confirmation is done outside of OSPFM
                                # Another process must read the database and
                                # send confirmation emails
                                randomhash = os.urandom(8).encode('hex')
                                db.session.add(
                                    models.UserEmail(
                                        user_username = self.username,
                                        email_address = address,
                                        confirmation = randomhash
                                    )
                                )
                    if 'remove' in emails and type(emails['remove'])==type([]):
                        for address in emails['remove']:
                            if address in previous_emails:
                                db.session.delete(
                                    models.UserEmail.query.filter(
                                        db.and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                        )
                                    ).first()
                                )
                    if 'enablenotifications' in emails and \
                       type(emails['enablenotifications']) == type([]):
                        for address in emails['enablenotifications']:
                            if address not in previous_notifications:
                                models.UserEmail.query.filter(
                                    db.and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                    )
                                ).first().notification = True
                    if 'disablenotifications' in emails and \
                       type(emails['disablenotifications']) == type([]):
                        for address in emails['disablenotifications']:
                            if address in previous_notifications:
                                models.UserEmail.query.filter(
                                    db.and_(
                               models.UserEmail.user_username == self.username,
                               models.UserEmail.email_address == address
                                    )
                                ).first().notification = False


            db.session.commit()
            return self.read(username)
        else:
            self.forbidden('The only user you can modify is yourself')

    def delete(self, username):
        self.forbidden('A user cannot be deleted with the API')

    def __search(self, substring):
        """Search on parts of the users name or on exact email address"""
        if len(substring) < 3:
            self.badrequest('Please give at least 3 characters')
        if '@' in substring:
            corresponding_rows = models.User.query.join(
                                    models.UserEmail
            ).filter(
                models.UserEmail.email_address == substring,
                models.UserEmail.confirmation == 'OK'
            )
        else:
            substring='%{0}%'.format(substring)
            corresponding_rows = models.User.query.filter(
                db.and_(
                    models.User.username != self.username,
                    db.or_(
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
                        db.joinedload(models.UserContact.contact)
        ).filter(
                        models.UserContact.user_username == self.username
        )
        return [c.as_dict() for c in contacts.all()]

    # TODO: Refuse new contacts unless at least one UserEmail is validated
    def create(self):
        if not 'username' in self.args:
            self.badrequest("Please provide the contact username")
        if self.username in config.DEMO_ACCOUNTS:
            self.badrequest("Cannot add contacts to demo accounts")
        # Verify the contact exists
        contactuser = models.User.query.filter(
                        models.User.username == self.args['username']
                      ).first()
        if not contactuser:
            self.notfound('This user does not exist')
        # Verify the user doesn't already have this contact
        testcontact = models.UserContact.query.filter(
                        db.and_(
                            models.UserContact.user_username == self.username,
                   models.UserContact.contact_username == self.args['username']
                        )
                      ).first()
        if testcontact:
            self.badrequest("This contact already exists")
        contact = models.UserContact(
                    user_username=self.username,
                    contact=contactuser,
                    comment=self.args.get('comment', '')
                  )
        db.session.add(contact)
        db.session.commit()
        return contact.as_dict()

    def read(self, username):
        contact = models.UserContact.query.filter(
            db.and_(
                models.UserContact.user_username == self.username,
                models.UserContact.contact_username == self.args['username']
            )
        ).first()
        if not contact:
            self.notfound('This contact does not exist')
        return contact.as_dict()

    def update(self, username):
        contact = models.UserContact.query.filter(
            db.and_(
                models.UserContact.user_username == self.username,
                models.UserContact.contact_username == self.args['username']
            )
        ).first()
        if not contact:
            self.notfound('Nonexistent contact cannot be modified')
        # Only the comment can be updated
        if 'comment' in self.args:
            contact.comment = self.args['comment']
            db.session.commit()
        return contact.as_dict()

    def delete(self, username):
        contact = models.UserContact.query.filter(
                    db.and_(
                        models.UserContact.user_username == self.username,
                        models.UserContact.contact_username == username
                    )
        ).first()
        if not contact:
            self.notfound('Nonexistent contact cannot be deleted')
        db.session.delete(contact)
        db.session.commit()
