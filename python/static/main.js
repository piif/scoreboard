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

// current ajax poll pending on server
var currentPoll = null;

// list of chrono times per game category
var chronoList = null;

// current mute state
var buzzer = undefined;

function iconpath(action) {
	return '/static/img/' + action + '.png';
}

function setError(msg) {
	$("#message").html(msg);
	setTimeout(function () { $("#message").html(""); }, 2000);
}

// send data to server
function send(action, errorMessage) {
	$.ajax({
		url: action,
		type: 'GET',
		cache: false,
		error: function(xhr, status, error) {
			setError((errorMessage == undefined ? "error" : errorMEssage) + " : " + status + "/" + error);
		}
	});
}

// continuously long poll server
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

// handle content returned by server polling
function handleMessage(data) {
	console.log(data);
	for (k in data) {
		if (k == 'error') {
			setError(data[k])
		} else if (k == 'buzzer' && data[k] !== buzzer) {
			mute(data[k]);
		} else if (k == 'timeout') {
			playpauseTimeout(data[k]);
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

// handle "mute" setting change
// 'state' unset means to toggle current value
var mute = function(state) {
	if (state != undefined) {
		buzzer = state;
	}
	if (buzzer) {
		buzzer = true;
		$("#buzz").attr('src', iconpath('unmute'));
		updateSettingsButton('buzzer', 'désactiver buzzer', 'mute');
	} else {
		buzzer = false;
		$("#buzz").attr('src', iconpath('mute'));
		updateSettingsButton('buzzer', 'activer buzzer', 'unmute');
	}
};

// handle "playpause" button
var playpause = function(state, doSend) {
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
};

// handle "timeout" button
var playpauseTimeout = function(state) {
	var t = $("#timeout");
	if (state === undefined) {
		state = t.hasClass('stopped')
	}
	if (state) {
		t.addClass('play').removeClass('stopped');
	} else {
		t.removeClass('play').addClass('stopped');
	}
}

// handle layout setting change
// 'vertical' unset means to toggle current value
var setLayout = function(vertical) {
	var body = $("body")
	if (vertical === undefined) {
		vertical = body.hasClass("vertical")
	}
	if (vertical) {
		body.removeClass("vertical");
		updateSettingsButton('layout', 'mode portrait', 'layout_v');
	} else {
		body.addClass("vertical");
		updateSettingsButton('layout', 'mode paysage', 'layout_h');
	}
}

// create a block with label, value and +/- buttons
function scoreButton(prefix, name, len) {
	var html = $('<div>')
		.addClass('digitsblock')
		.attr('id', name+'_block');
	html.append(
		prefix
	,
		// "+" is before "-" but displayed on right of inout by "rtl" direction of outer div
		// with this ugly hack, in vertical layout, "+" stays on top and "-" at bottom
		$('<img>')
			.addClass('plus')
			.attr('src', iconpath('plus'))
			.attr('id', name+'_plus')
			.attr('rel', name)
			.attr('title', '+')
	,
		$('<input>')
			.addClass('digits')
			.attr('type', 'text')
			.attr('id', name)
			.attr('size', len)
			.val('_'.repeat(len))
	,
		$('<img>')
			.addClass('minus')
			.attr('src', iconpath('minus'))
			.attr('id', name+'_minus')
			.attr('rel', name)
			.attr('title', '-')
	);

	return html;
}

// callback for +/- buttons
function changeValue(rel, target, delta) {
	var value = parseInt(target.val());
	if (delta != null) {
		value += delta;
	}

	send('/' + rel + '/' + value, "Impossible de fixer " + rel + " à " + value);
	target.addClass('waiting').removeClass('onscreen');
}

function addHeaderButton(action, label, onclick) {
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
			.attr('title', label)
			.addClass(action)
			.click(onclick)
	);
}

function addSettingsButton(action, label, onclick) {
	if (onclick == undefined) {
		onclick = function(){
			$('.digits').addClass('waiting').removeClass('onscreen');
			send('/' + action, "Erreur sur " + action);
		};
	}
	$('#settingsMenu').append(
		$('<div>').append(
			$('<label>' + label + '</label>')
		,
			$('<img>')
				.attr('src', iconpath(action))
				.attr('id', action)
				.attr('title', label)
				.addClass(action)
				
		).click(function() {
			onclick();
			$('#settingsMenu').hide();
		})
	);
}

function updateSettingsButton(action, label, icon) {
	var img = $("#" + action);
	img.attr('src', iconpath(icon));
	$('label', img.parent()).text(label);
}

// create buttons for each period durations in timelist current value
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
					send('/setchrono/' + time, "Erreur au démarrage du chrono");
				})
			);
		}
	}
}

// create chronos toolbar : buzz, time and playpause button
function addChrono() {
	$('#chrono').append(
		// buzz button
		$('<img>')
			.attr('id', 'buzz')
			.attr('src', iconpath('buzzer'))
			.attr('title', 'buzz')
			.addClass('buzz')
			.click(function() {
				if (buzzer) {
					send('/buzz');
				}
			})
		,
		// time list
		$('<select>')
			.attr('id', 'timelist')
			.change(updateTimeList)
		,
		// start buttons
		$('<span>')
			.attr('id', 'startbuttons')
		,
		$('<span>').append(
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
		)
		,
		$('<span>').append(
			// pause / play
			$('<img>')
				.attr('id', 'playpause')
				.attr('src', iconpath('play'))
				.attr('title', 'play')
				.addClass('play')
				.click(function() {
					playpause($(this).hasClass('pause') ? "pause" : "play");
				})
			,
			// time out call button
			$('<img>')
				.attr('id', 'timeout')
				.attr('src', iconpath('timeout'))
				.attr('title', 'timeout')
				.addClass('stopped')
				.click(function() {
					send('/timeout');
					playpause("pause");
				})
		)
	);
}

$( document ).ready(function() {
	// TODO : test this code, from
	// http://stackoverflow.com/questions/4917664/detect-viewport-orientation-if-orientation-is-portrait-display-alert-message-ad
	// Listen for orientation changes
	window.addEventListener("orientationchange", function() {
		if (window.orientation === 0) {
			setLayout(false);
		} else {
			setLayout(true);
		}
	}, false);


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
	// get times menu
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

	// handle every +/- buttons
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
	// and direct inputs
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

	// buttos on top of page
	addHeaderButton('refresh', 'rafraichir');
	addHeaderButton('settings', 'paramêtres', function() {
		$('#settingsMenu').toggle();
	});

	// and buttons in settings menu
	$('#settingsMenu').hide();
	addSettingsButton('reload', 'recharger', function() {
		window.location = window.location.href;
	});
	addSettingsButton('test', 'test écran');
	addSettingsButton('blank', 'écran éteint');

	addSettingsButton('buzzer', 'buzzer', function() {
		send('/buzzer/' + (buzzer ? "off" : "on"));
	});

	addSettingsButton('layout', 'layout', setLayout);
	if (window.orientation === 0) {
		setLayout(false);
	} else {
		setLayout(true);
	}
	addSettingsButton('reset', 'remise à 0', function() {
		if (confirm("Tout ré-initialiser ?")) {
			send('/reset', "Can't reset");
		}
	});

	addSettingsButton('shutdown', 'éteindre la console', function() {
		if (confirm("Éteindre l'écran et la console ?")) {
			send('/shutdown', "Can't shutdown");
		}
	});

	addSettingsButton('language', 'langue', function() {
		alert("Todo ...");
	});

	addSettingsButton('password', 'mot de passe wifi', function() {
		$("#changepasswordwrapper").show();
	});

	addSettingsButton('upgrade', 'mise à jour', function() {
		window.location = "/upgrade.html";
	});

	// password change "popup"
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

	// finally, launch polling
	poll('/poll');
	// and force a first refresh to get initial values
	send('/refresh');
});
