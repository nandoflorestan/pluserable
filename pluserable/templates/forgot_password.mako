<html>
  <body>
    <div class="flash-messages">
        % for msg in request.session.pop_flash():
            ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
        % endfor
    </div>

    <h1>Forgot Password</h1>
    ${form|n}
  </body>
</html>

