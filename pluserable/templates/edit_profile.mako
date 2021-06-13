<html>
  <body>
    <a href="${request.route_url('index')}">Back to Index</a>

    <div class="flash-messages">
        % for msg in request.get_flash_msgs():
            ${msg_to_html(flavor='bootstrap3', msg=msg)|n}
        % endfor
    </div>

    <h1>Profile</h1>
    ${form|n}
  </body>
</html>
