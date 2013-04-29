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

from ospfm import db, helpers
from ospfm.core import currency as currencylib
from ospfm.core import models as core
from ospfm.transaction import models
from ospfm.objects import Object


class Category(Object):

    def __own_category(self, categoryid):
        return models.Category.query.options(
                        db.joinedload(models.Category.currency)
               ).filter(
                    db.and_(
                        models.Category.owner_username == self.username,
                        models.Category.id == categoryid
                    )
               ).first()

    def list(self):
        categories = models.Category.query.order_by(
                        models.Category.name
                     ).options(
                        db.joinedload(models.Category.currency)
                     ).filter(
                        db.and_(
                            models.Category.owner_username == self.username,
                            models.Category.parent_id == None
                        )
                     ).all()
        return [c.as_dict(self.username) for c in categories]

    def create(self):
        if not ('currency' in self.args and 'name' in self.args):
            self.badrequest()
        if 'parent' in self.args:
            parent = self.__own_category(self.args['parent'])
            if not parent:
                self.badrequest()
        else:
            parent = None
        currency = core.Currency.query.filter(
            db.and_(
                core.Currency.isocode == self.args['currency'],
                db.or_(
                    core.Currency.owner_username == self.username,
                    core.Currency.owner_username == None
                )
            )
        ).first()
        if not currency:
            self.badrequest()
        category = models.Category(
                        owner_username=self.username,
                        parent=parent,
                        currency=currency,
                        name=self.args['name']
                   )
        db.session.add(category)
        db.session.commit()
        return category.as_dict(self.username)

    def read(self, categoryid):
        category = self.__own_category(categoryid)
        if category:
            return category.as_dict(self.username)
        self.notfound()

    def update(self, categoryid):
        category = self.__own_category(categoryid)
        if not category:
            self.notfound()
        if 'name' in self.args:
            category.name = self.args['name']
        if 'currency' in self.args:
            currency = core.Currency.query.filter(
                db.and_(
                    core.Currency.isocode == self.args['currency'],
                    db.or_(
                        core.Currency.owner_username == self.username,
                        core.Currency.owner_username == None
                    )
                )
            ).first()
            if currency:
                rate = helpers.rate(
                            self.username,
                            category.currency.isocode,
                            currency.isocode
                       )
                category.currency = currency
                for tc in models.TransactionCategory.query.filter(
                            models.TransactionCategory.category == category
                          ).all():
                    tc.category_amount = tc.category_amount * rate
        if 'parent' in self.args:
            if self.args['parent'] == 'NONE':
                category.parent_id = None
            else:
                parent = self.__own_category(self.args['parent'])
                if not parent:
                    self.badrequest()
                if category.contains_category(parent.id):
                    self.badrequest()
                if parent.id != category.parent_id:
                    allparents = set([parent.id, category.parent_id] + \
                                     parent.all_parents_ids())
                    if category.parent_id:
                        allparents.update(category.parent.all_parents_ids())
                    for parentid in allparents:
                        if parentid:
                            self.add_to_response('categoriesbalance', parentid)
                    category.parent = parent
        db.session.commit()
        return category.as_dict(self.username)

    def delete(self, categoryid):
        category = self.__own_category(categoryid)
        if not category:
            self.notfound()
        db.session.delete(category)
        db.session.commit()
