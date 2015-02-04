// REF: https://github.com/mleibman/SlickGrid/wiki/Examples
// Example: https://github.com/mleibman/SlickGrid/blob/gh-pages/examples/example3-editing.html
// http://mleibman.github.io/SlickGrid/examples/example3-editing.html
function requiredFieldValidator(value) {
    if (value == null || value == undefined || !value.length) {
      return {valid: false, msg: "This is a required field"};
    } else {
      return {valid: true, msg: null};
    }
  }

  var grid;
  var data = [];
  //width: 60, 
  var columns = [
    {id: "option-id", name: "Option ID", field: "option-id", cssClass: "cell-title"}, // width: 60, 
    //{id: "freely-respond", name: "Respond Free Text", cssClass: "cell-freely-respond", field: "freely-respond", formatter: Slick.Formatters.Checkmark, editor: Slick.Editors.Checkbox},
    {id: "keyword", name: "Trigger Word", field: "keyword", cssClass: "cell-title", editor: Slick.Editors.Text, validator: requiredFieldValidator},
    {id: "separator", name: "Separator", field: "separator", editor: Slick.Editors.Text, validator: requiredFieldValidator},
    {id: "option-text", name: "Option Text", field: "option-text", width: 450, editor: Slick.Editors.LongText},
    {id: "our-response", name: "Our Response", field: "our-response", width: 450, editor: Slick.Editors.LongText},
    //{id: "add-option-button", name: "Add Option Button", width: 80, formatter: buttonGenerator},
  ];
  
  var options = {
    editable: true,
    enableAddRow: true,
    enableCellNavigation: true,
    asyncEditorLoading: false,
    autoEdit: true,
    autoHeight:true,
    forceFitColumns: true,
    autoWidth: true,
  };
  
  var buttonGenerator = function () {
    s ="<a href='" + '#' + '">' + "</a>";
    return  s;
  };