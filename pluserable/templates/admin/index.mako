<%inherit file="pluserable:templates/layout.mako"/>

<a href="${request.route_url('admin_users_create')}">Create New User</a>

<ul>
  <li><a href="${request.route_url('admin_users_index')}">User List</a></li>
</ul>
