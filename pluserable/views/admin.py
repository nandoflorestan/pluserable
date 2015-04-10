# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import deform
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from ..interfaces import IUserClass
from ..forms import PluserableForm
from ..lib import FlashMessage
from ..resources import RootFactory
from ..schemas import EmailAdminUserSchema, UsernameAdminUserSchema
from ..views import BaseController


@view_defaults(permission='group:admin')
class AdminController(BaseController):
    @view_config(
        route_name='admin_users_create',
        renderer='pluserable:templates/admin/create_user.mako'
    )
    @view_config(
        route_name='admin_users_edit',
        renderer='pluserable:templates/admin/create_user.mako'
    )
    def create_user(self):
        User = self.request.registry.queryUtility(IUserClass)
        schema = UsernameAdminUserSchema() if hasattr(
            User, 'username') else EmailAdminUserSchema()
        schema = schema.bind(request=self.request)
        form = PluserableForm(schema)

        if self.request.method == 'GET':
            if isinstance(self.request.context, RootFactory):
                return dict(form=form)
            else:
                return dict(
                    form=form,
                    appstruct=self.request.context.__json__(self.request)
                )
        else:
            try:
                controls = self.request.POST.items()
                captured = form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(form=e, errors=e.error.children)

            del captured['csrf_token']
            if isinstance(self.request.context, RootFactory):
                user = self.User(**captured)
            else:
                user = self.request.context
            if captured['password']:
                user.password = captured['password']
            self.db.add(user)
            FlashMessage(self.request, self.Str.admin_create_user_done,
                         kind='success')
            return HTTPFound(
                location=self.request.route_url('admin_users_index')
            )

    @view_config(
        route_name='admin',
        renderer='pluserable:templates/admin/index.mako'
    )
    def index(self):
        return {}

    @view_config(
        route_name='admin_users_index',
        renderer='pluserable:templates/admin/users_index.mako'
    )
    def users_index(self):
        return dict(users=self.User.get_all(self.request))
