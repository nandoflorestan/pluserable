<html>
  <body>

    <div class="flash-messages">
        % for msg in request.get_flash_msgs():
            ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
        % endfor
    </div>

    <h1>Reset Password</h1>
    ${form|n}
    <p>Don't have an account? <a href="${request.route_url('register')}">Sign up!</a></p>
  </body>
</html>

