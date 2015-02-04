// This was used in selecting groups based on schools. But now it is not necessary.
// Saving this in case we need similar function in the future.
$(function() {
		function update_group_ids() {
			// get all selected groups ids
			var group_ids = [];
			$('#selected_groups li').each(function(){
				group_ids.push($(this).attr('value'));
			});
			$('#selected_group_ids').val(group_ids.join(','));
		}
		
		$('#add-group').on('click', function(e) {
			group_id = $('#groups').children(":selected").attr("value");
			tag = "#selected_groups li[value='" + group_id + "']";
			// check the selected groups, if the li with value groupp_id
			if ($(tag).length){
				 alert('You already added this group');
				 return;
			}
	        if ($('#groups option').length != 0){
	        	group_name = $('#groups').children(":selected").text();	        	
	        	school_name = $('#schools').children(":selected").text();
	        	txt = school_name + '--' + group_name;
	        	$('#selected_groups').append($("<li></li>").attr("value",group_id).text(txt));
	        	update_group_ids();
	        }
	        //if ($(#groups).children(":selected").attr("value"))
    		//<li value="">School-group <a href='#'>Remove</a></li>

	    });
	
		$("#schools").change(function() {
			
			// first remove all existing optoins
			$("#groups option").remove();
			
		  	var id = $(this).children(":selected").attr("value");
		  	if (id == '')	return;

		  	$.ajax({
				url : "{% url 'organizations:search_group' %}",
				dataType : "json",
				data : {
					school_id: id,
				},
				success : function(data) {
					
					$.each(data, function(key, value) {
						$('#groups').append($("<option></option>").attr("value",value.id).text(value.name)); 
					});

				}
			});
		});
});
