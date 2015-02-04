// This was used in selecting groups based on schools. But now it is not necessary.
// Saving this in case we need similar function in the future.
$(function() {
	
	function remove_listed_members(){
		$('#members').empty();
	}
	
	
	function update_selected_numbers(){
		var nums = [];
		$('#selected-members li').each(function(){
			nums.push($(this).data('phone'));
		});
		
		$('#id_phone_numbers').val(nums.join(','));
	}
	
	
	function already_been_added(new_num){
		var existed = false;
		$('#selected-members li').each(function(){
			if (existed || new_num == $(this).data('phone')){
				existed = true;
			}
		});
		return existed;
	}	
	
	$('#select-member-button').click(function(){
		$( "#members option:selected" ).each(function() {
			
			if (already_been_added($(this).val())){
				return;
			}

			//var $list = $('<li>').attr('class', 'list-group-item').data('phone', $(this).val()); // if we are to use bootstrap's list group
			var $list = $('<li>').data('phone', $(this).val()); // save phone number to custom data field first
			var str = $(this).text() + ' [';
			$list.text(str).append($('<a href="javascript:void(0);">').text('Remove'));
			$list.find('a').after(']');
			$('#selected-members').append($list);
			
			update_selected_numbers();		
		});
	});
	

	$(document).on('click', '#selected-members li a', function(){
		$(this).parent().remove();
		update_selected_numbers();
	});
	

	$("#schools").change(function() {
		remove_listed_members();

    	var school_id = $(this).val();
    	    	
    	if (school_id.length == 0){
    		return;
    	}
    	
		$.ajax({
			url : "/organizations/list_members_by_school/",
			//url : "{% url 'organizations:list_members_by_school' %}",
			dataType : "json",
			data: {school_id : school_id},
			success : function(data) {
				$.each(data, function(index, item){
					var $option = $('<option>').attr('value', item.phone_num).text(item.phone_num + ' (' + item.role + ', ' + item.school + ')');
					$('#members').append($option);
				});
			}
		});
	});

});
