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

from ospfm import db
from ospfm.core import models
from ospfm.objects import Object


class Preference(Object):

    def __own_preference(self, preferencename):
        return models.UserPreference.query.filter(
                    db.and_(
                        models.UserPreference.user_username == self.username,
                        models.UserPreference.name == preferencename
                    )
               ).first()

    def list(self):
        preferences = models.UserPreference.query.options(
                      ).filter(
                        models.UserPreference.user_username == self.username
                      ).all()
        return [p.as_dict() for p in preferences]

    def create(self):
        # Do not "create" preferences, just update them...
        self.forbidden(
      'Please update the preference: if it does not exist, it will be created')

    def read(self, preferencename):
        preference = self.__own_preference(preferencename)
        if preference:
            return preference.as_dict()
        else:
            return {'name':preferencename, 'value':'UNSET'}

    def update(self, preferencename):
        preference = self.__own_preference(preferencename)
        if not preference:
            preference = models.UserPreference(
                user_username = self.username,
                name = preferencename
            )
            db.session.add(preference)
        preference.value = self.args['value']
        db.session.commit()
        return preference.as_dict()

    def delete(self, preferencename):
        preference = self.__own_preference(preferencename)
        if not preference:
            self.notfound('Nonexistent preference cannot be deleted')
        db.session.delete(preference)
        db.session.commit()
