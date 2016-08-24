// light version of https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/String/repeat
if (!String.prototype.repeat) {
	String.prototype.repeat = function (count) {
		var str = "" + this , res = "";
		if (count == 0 || str.length == 0) {
			return "";
		}
		while(count--) {
			res += str;
		}
		return res;
	}
}

var currentPoll = null;

var chronoList = null;

function iconpath(action) {
	return '/static/img/' + action + '.png';
}

function setError(msg) {
	$("#message").html(msg);
	setTimeout(function () { $("#message").html(""); }, 2000);
}

function poll() {
	var poll_interval=100;
	currentPoll = $.ajax({
		url: "/poll",
		type: 'GET',
		cache: false,
		dataType: 'json',
		timeout: 30000,
		success: function(data) {
			handleMessage(data);
			poll_interval=0;
		},
		error: function (xhr, status, error) {
			poll_interval=1000;
			setError("Poll error : " + status + "/" + error);
		},
		complete: function () {
			setTimeout(poll, poll_interval);
		},
	});
}
function handleMessage(data) {
	console.log(data);
	for (k in data) {
		if (k == 'error') {
			setError(data[k])
		} else {
			$('#'+k)
				.val(data[k])
				.removeClass('waiting').addClass('onscreen');
		}
	}
	if (data.Minutes === 0 && data.Seconds === 0) {
		playpause("pause", false);
	}
	//$('#message').html("<pre>message " + JSON.stringify(data) + "</pre>");
}

playpause = function(state, doSend) {
	if (state === "pause") {
		if (doSend !== false) {
			// send pause
			send('/pause', "Erreur sur arrêt chrono");
		}
		// set icon to 'unpause'
		$("#playpause")
			.removeClass('pause').addClass('play')
			.attr('src', iconpath('play'))
			.attr('title', 'play')
	} else if (state === "play") {
		if (doSend !== false) {
			// send unpause
			send('/play', "Erreur sur redémarrage chrono");
		}
		// set icon to 'pause'
		$("#playpause")
			.addClass('pause').removeClass('play')
			.attr('src', iconpath('pause'))
			.attr('title', 'pause')
	}
}

function scoreButton(prefix, name, len) {
	var html = $('<div>')
		.addClass('digitsblock')
		.attr('id', name+'_block');
	html.append(
		prefix
	,
		$('<img>')
			.addClass('minus')
			.attr('src', iconpath('minus'))
			.attr('id', name+'_minus')
			.attr('rel', name)
			.attr('title', '-')
	,
		$('<input>')
			.addClass('digits')
			.attr('type', 'text')
			.attr('id', name)
			.attr('size', len)
			.val('_'.repeat(len))
	,
		$('<img>')
			.addClass('plus')
			.attr('src', iconpath('plus'))
			.attr('id', name+'_plus')
			.attr('rel', name)
			.attr('title', '+')
	);

	return html;
}

function addHeaderButton(action, onclick) {
	if (onclick == undefined) {
		onclick = function(){
			$('.digits').addClass('waiting').removeClass('onscreen');
			send('/' + action, "Erreur sur " + action);
		};
	}
	$('#header').append(
		$('<img>')
			.attr('src', iconpath(action))
			.attr('id', action)
			.attr('title', action)
			.addClass(action)
			.click(onclick)
	);
}
function addSettingsButton(action, onclick) {
	if (onclick == undefined) {
		onclick = function(){
			$('.digits').addClass('waiting').removeClass('onscreen');
			send('/' + action, "Erreur sur " + action);
		};
	}
	$('#settingsMenu').append(
		$('<div>').append(
			$('<label>' + action + '</label>')
		,
			$('<img>')
				.attr('src', iconpath(action))
				.attr('id', action)
				.attr('title', action)
				.addClass(action)
				
		).click(function() {
			onclick();
			$('#settingsMenu').hide();
		})
	);
}

function updateTimeList() {
	var value = $("#timelist").val();
	if (value == "manuel") {
		$("#startbuttons").html("");
	} else {
		var newList = chronoList[value];
		console.log(newList);
		$("#startbuttons").html('')
		for (period in newList) {
			$("#startbuttons").append( $('<input>')
				.attr('type', 'button')
				.attr('id', 'start_' + period)
				.attr('rel', newList[period])
				.val(period)
				.addClass('start')
				.click(function() {
					var time = $(this).attr('rel');
					send('/start/' + time, "Erreur au démarrage du chrono");
					playpause("play");
				})
			);
		}
	}
}

function addChrono() {
	$('#chrono').append(
		// time list
		$('<select>')
			.attr('id', 'timelist')
			.change(updateTimeList)
		,
		// start buttons
		$('<span>')
			.attr('id', 'startbuttons')
		,
		// digits
		$('<input>')
			.attr('type', 'number')
			.attr('id', 'Minutes')
			.attr('min', '0').attr('max', '99')
			.attr('size', '2')
			.val('__')
			.addClass('digits')
		,
		$('<span> : </span>')
		,
		$('<input>')
			.attr('type', 'number')
			.attr('id', 'Seconds')
			.attr('min', '0').attr('max', '59')
			.attr('size', '2')
			.val('__')
			.addClass('digits')
		,
		// pause / play
		$('<img>')
			.attr('id', 'playpause')
			.attr('src', iconpath('play'))
			.attr('title', 'play')
			.addClass('play')
			.click(function() {
				playpause($(this).hasClass('pause') ? "pause" : "play");
			})
	);
}

$( document ).ready(function() {
	// add scores button
	$('#scores').append(
		$("<div><label>Locaux</label></div>").append(
			scoreButton('<label>fautes</label>', 'FL', 1),
			scoreButton('<label>buts</label>', 'BL', 2)
		),
		$("<div><label>Visiteurs</label></div>").append(
			scoreButton('<label>fautes</label>', 'FV', 1),
			scoreButton('<label>buts</label>', 'BV', 2)
		)
	);

	addChrono();
	$.ajax({
		url: "/chronos",
		type: 'GET',
		dataType: 'json',
		success: function(data) {
			chronoList = data;
			list = $("#timelist");
			list.append( $("<option>").val("manuel").text("manuel") );
			for (lbl in data) {
				list.append( $("<option>").val(lbl).text(lbl) );
			}
		},
		error: function (xhr, status, error) {
			setError("Erreur au chargement de la liste des temps : " + status + "/" + error);
		}
	});

	// handle +/-
	$('.plus').click(function() {
		var rel = $(this).attr('rel');
		var target = $('#'+rel)
		changeValue(rel, target, 1);
	});
	$('.minus').click(function() {
		var rel = $(this).attr('rel');
		var target = $('#'+rel)
		changeValue(rel, target, -1);
	});
	// and direct input
	$('.digits')
		.focus(function() {
			$(this).removeClass('waiting').removeClass('onscreen');
		})
		.change(function() {
			var target = $(this);
			var rel = target.attr('id')
			changeValue(rel, target);
		}
	);

	addHeaderButton('refresh');

	$('#settingsMenu').hide();
	addHeaderButton('settings', function() { $('#settingsMenu').toggle(); });

	addSettingsButton('reload', function(){
		window.location.reload();
	});
	addSettingsButton('test');
	addSettingsButton('blank');
	addSettingsButton('reset', function() {
		if (confirm("Tout ré-initialiser ?")) {
			send('/reset', "Can't reset");
		}
	});

	addSettingsButton('shutdown', function() {
		if (confirm("Éteindre l'écran et la console ?")) {
			send('/shutdown', "Can't shutdown");
		}
	});

	addSettingsButton('language', function() {
		alert("Todo ...");
	});

	$("#changepasswordwrapper").hide();
	$("#password_cancel").click(function() { $("#changepasswordwrapper").hide(); });
	$("#password_ok").click(function() {
		var oldpass = $("#oldpass").val()
		var newpass = $("#newpass1").val()
		if(newpass != $("#newpass2").val()) {
			alert("nouveau mot de passe et confirmation diffèrent");
			return;
		}
		if (newpass.length < 8) {
			alert("Le nouveau mot de passe doit faire au moins 8 caractères");
			return;
		}
		send("/password/" + oldpass + ":" + newpass);
		$("#changepasswordwrapper").hide();
	});
	addSettingsButton('password', function() {
		$("#changepasswordwrapper").show();
	});

	addSettingsButton('upgrade', function() {
		alert("Todo ...");
	});

	poll('/poll');
	send('/refresh');
});

function toggleSettings() {
	console.log("Todo ...")
}

function changeValue(rel, target, delta) {
	var value = parseInt(target.val());
	if (delta != null) {
		value += delta;
	}

	send('/' + rel + '/' + value, "Impossible de fixer " + rel + " à " + value);
	target.addClass('waiting').removeClass('onscreen');
}

function send(action, errorMessage) {
	$.ajax({
		url: action,
		type: 'GET',
		cache: false,
		error: function(xhr, status, error) {
			setError(errorMessage + " : " + status + "/" + error);
		}
	});
}
