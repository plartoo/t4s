$(function() {
	function log(message) {
		$("<div>").text(message).prependTo("#log");
		$("#log").scrollTop(0);
	}

	function update_remaining_char(){
		$('#char_left').text(CHAR_LIMIT - cur_msg_len - $(this).val().length - $('#id_trigger_keyword').val().length);	 
		return false;	
	}

	$("#message").autocomplete({
		source : function(request, response) {
			$.ajax({
				url : "/messages/search",
				dataType : "json",
				data : {
					keyword: $('#message').val(),
					msg_id: $('#parent_msg_id').val()
				},
				success : function(data) {
					response($.map(data, function(item) {
						return {
							label : item.content,
							value : item.id
						}
					}));
				}
			});
		},
		minLength : 5,
		 select : function(event, ui) {
		 	$( "#message" ).val( ui.item.label );
		 	$( "#id_child_msg" ).val( ui.item.value );
		 	return false;
		 },
	});

	// making sure user selects the one that is brought up by auto complete
	$('#message').keydown(function(){
		$('#id_child_msg').val('');
	});
	
	var CHAR_LIMIT = 160;
	var cur_msg_len = $("#current-msg").text().length;

	$('#id_option_content').keyup(update_remaining_char);
	$('#id_trigger_keyword').keyup(update_remaining_char);
});


