<%inherit file="pluserable:templates/layout.mako"/>

% for user in users:
  ${user.email} [<a href="${request.route_url('admin_users_edit', user_id=user.id)}">Edit</a>]
% endfor
