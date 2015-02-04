var grid;  // global

$(document).ready(function(){
	var continue_btn = "<button type='button' class='btn btn-small btn-link continue-btn'>Continue converastion after this reply</button>";
	//var delete_btn = "<button type='button' class='btn btn-link remove-btn'><span class='label label-danger remove-label'>Remove option</span></button>";
	var delete_btn = "<button type='button' class='btn btn-small btn-link remove-btn'>Remove option</button>";
	
	// Ref: http://stackoverflow.com/questions/17444408/how-to-add-a-cutom-delete-option-for-backgrid-rows
	var DeleteCell = Backgrid.Cell.extend({
		
	    template: _.template(delete_btn),
	    events: {
	      "click": "deleteRow"
	    },
	    deleteRow: function (e) {
	      e.preventDefault();
	      if(confirm('Are you sure you want to delete this option?')){
	     	this.model.collection.remove(this.model);
	     	row_count--;
	     	cur_height = $('#backgrid-table').height();
			$('#backgrid-table').height(cur_height - row_height);
	      }
	    },
	    render: function () {
	      this.$el.html(this.template());
	      this.delegateEvents();
	      return this;
	    }
	});

	var ContinueCell = Backgrid.Cell.extend({
		
	    template: _.template(continue_btn),
	    events: {
	      "click": "continueOption"
	    },
	    continueOption: function (e) {
	      e.preventDefault();
	      if (this.model.attributes.child_msg_id) { // To prevent event being triggered when clicking empty cell
	      	submit(add_option_url, this.model.attributes.child_msg_id);
	      }
	    },
	    render: function (e) {
	      if (this.model.attributes.id){
		      this.$el.html(this.template());
	      }
	      else{	// if this row has not been submitted, we'll not show continue button
	      	  this.$el.html('');
	      }
	      this.delegateEvents();
	      return this;
	    }
	});


	var Option = Backbone.Model.extend({});
	var Options = Backbone.Collection.extend({
	  model: Option,
	});

	var options = new Options();
	options.add(default_options);

	var selectVals = [{name: 'Separators', values: [['None', ''], [' ', ' '], [')', ')'], ['-', '-']]}];
	
	var columns = [{
	    name: "keyword",
	    label: "Letter Choice or KEYWORD",
	    // The cell type can be a reference of a Backgrid.Cell subclass, any Backgrid.Cell subclass instances like *id* above, or a string
	    cell: "string" // This is converted to "StringCell" and a corresponding class in the Backgrid package namespace is looked up
	  }, {
	    name: "separator",
	    label: "Separating Character",
	    cell: Backgrid.SelectCell.extend({
	    	optionValues: selectVals
	    })
	    //optionValues:  nums,
	  }, {
	    name: "option_text",
	    label: "Text to appear after letter or KEYWORD (blank if none)",
	    cell: "string" // An integer cell is a number cell that displays humanized integers
	  }, {
	    name: "reply",
	    label: "Our reply back",
	    cell: "string" // A cell type for floating point value, defaults to have a precision 2 decimal numbers
	  }, {
	  	name: "continue",
		label: "",
		cell: ContinueCell
	  }, {
	  	name: "delete",
		label: "",
		cell: DeleteCell
	  }];
	
	// Initialize a new Grid instance
	grid = new Backgrid.Grid({
	  columns: columns,
	  collection: options,
	  className: "table table-bordered",  
	});
	
	// Render the grid and attach the root to your HTML document
	$("#backgrid-table").append(grid.render().el);


});
