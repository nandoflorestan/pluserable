<html>
  <body>
    <a href="${request.route_url('index')}">Back to Index</a>

    <div class="flash-messages">
        % for msg in request.session.pop_flash():
            ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
        % endfor
    </div>

    <h1>Register</h1>
    ${form|n}
  </body>
</html>
