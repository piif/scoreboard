 <!DOCTYPE html>
 <html>
<head>
	<!--meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no"-->
	<title>ScoreBoard Upgrade Page</title>
    <link rel="stylesheet" href="/static/main.css" type="text/css" />

	<!--script src='/static/jquery-3.1.0.js'></script>
	<script src='/static/upgrade.js'></script-->
</head>
<body>
	<div id='header' class='title'>Tableau de scores: mise à jour</div>
	<div id='version'>version actuelle : {{currentVersion}}</div>

	<form id='changepassword' method='post' action='/' enctype='multipart/form-data'>
		<label>Fichier de mise à jour :</label> <input type='file' name='upgrade' />
		<div>
			<input type='submit' value='OK' name='action' />
			<input type='submit' value='cancel' name='action' />
		</div>
	</form>
</body>
</html>
