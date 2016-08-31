 <!DOCTYPE html>
 <html>
<head>
	<!--meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"-->
	<title>ScoreBoard Main Page</title>
    <link rel="stylesheet" href="/static/main.css" type="text/css" />

	<script src='/static/jquery-3.1.0.js'></script>
	<script src='/static/main.js'></script>
</head>
<body>
	<div id='headerwrapper'><div id='header'><span class='title'>Tableau de scores</span> <div id='settingsMenu'></div></div></div>
	<div id='chrono'></div>
	<div id='scores'></div>
	<div id='message'>{{message if defined("message") else ""}}</div>

	<div id='changepasswordwrapper'>
	<div id='changepassword'>
		<div><label>Ancien mot de passe wifi :</label>  <input type='password' size='12' id='oldpass'  /></div>
		<div><label>Nouveau mot de passe :</label>      <input type='password' size='12' id='newpass1' /></div>
		<div><label>Confirmation mot de passe :</label> <input type='password' size='12' id='newpass2' /></div>
		<input type='button' value='ok' id='password_ok' />
		<input type='button' value='cancel' id='password_cancel' />
	</div>
	</div>
</body>
</html>
