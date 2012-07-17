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

from sqlalchemy import and_

from ospfm.transaction import models
from ospfm.database import session
from ospfm.objects import Object


class Category(Object):

    def __own_category(self, categoryid):
        return models.Category.query.filter(
                    and_(
                        models.Category.owner_username == self.username,
                        models.Category.id == categoryid
                    )
               ).first()

    def list(self):
        categories = models.Category.query.order_by(
                        models.Category.name
                     ).filter(
                        and_(
                            models.Category.owner_username == self.username,
                            models.Category.parent_id == None
                        )
                     ).all()
        return [c.as_dict() for c in categories]

    def create(self):
        if self.args.has_key('parent'):
            parent = self.__own_category(self.args['parent'])
            if not parent:
                self.badrequest()
        else:
            parent = None
        category = models.Category(
                        owner_username=self.username,
                        parent=parent,
                        name=self.args['name']
                   )
        session.add(category)
        session.commit()
        return category.as_dict()

    def read(self, categoryid):
        category = self.__own_category(categoryid)
        if category:
            return category.as_dict()
        self.notfound()

    def update(self, categoryid):
        category = self.__own_category(categoryid)
        if not category:
            self.notfound()
        if self.args.has_key('name'):
            category.name = self.args['name']
        if self.args.has_key('parent'):
            if self.args['parent'] == 'NONE':
                category.parent_id = None
            else:
                parent = self.__own_category(self.args['parent'])
                if not parent:
                    self.badrequest()
                if category.contains_category(parent.id):
                    self.badrequest()
                category.parent = parent
        return category.as_dict()

    def delete(self, categoryid):
        category = self.__own_category(categoryid)
        if not category:
            self.notfound()
        session.delete(category)
        session.commit()
