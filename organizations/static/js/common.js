var CHAR_LIMIT = 160;

function update_char_left(cur_msg){
	var $char_left = $('.char-left');
	var char_remaining = CHAR_LIMIT - cur_msg.length;
	
	$char_left.text(char_remaining);

	if (char_remaining < 0){
		$('.char-left').addClass('warning');
	}
	else{
		$('.char-left').removeClass('warning');
	}
}

$(document).ready(function(){
	$('.help').tooltip(); // if there's any, activate tooltip
});
