function showFields() {
  var service_type = document.getElementById("service_type").value;
  document.getElementById("noc_details").style.display = "none";
  document.getElementById("sublease_details").style.display = "none";
  document.getElementById("water_requirment_details").style.display = "none";
  document.getElementById("eb_poll_details").style.display = "none";
  document.getElementById("surrender_approval_details").style.display = "none";
  document.getElementById("change_name_company_details").style.display = "none";
  document.getElementById("transfer_tags").style.display = "none";
  document.getElementById("other_services_details").style.display = "none";
  document.getElementById("reach_md_details").style.display = "none";
  document.getElementById("change_in_name_of_product").style.display = "none";
  document.getElementById("change_in_name_of_constitution").style.display = "none";
  document.getElementById("change_in_name_of_management").style.display = "none";

  if (service_type === "noc") {
    document.getElementById("noc_details").style.display = "block";
  } else if (service_type === "sublease") {
    document.getElementById("sublease_details").style.display = "block";
  } else if (service_type === "water_requirment") {
    document.getElementById("water_requirment_details").style.display = "block";
  } else if (service_type === "eb_poll") {
    document.getElementById("eb_poll_details").style.display = "block";
  } else if (service_type === "surrender") {
    document.getElementById("surrender_approval_details").style.display = "block";
  } else if (service_type === "change_company") {
    document.getElementById("change_name_company_details").style.display = "block";
  } else if (service_type === "transfer_of_lease_holds") {
    document.getElementById("transfer_tags").style.display = "block";
  }
  else if (service_type === "reach_md") {
    document.getElementById("reach_md_details").style.display = "block";
  }
  else if (service_type === "other_services") {
    document.getElementById("other_services_details").style.display = "block";
  }
  else if (service_type === "change_in_product") {
    document.getElementById("change_in_name_of_product").style.display = "block";
  }
  else if (service_type === "change_in_constitution") {
    document.getElementById("change_in_name_of_constitution").style.display = "block";
  }
  else if (service_type === "change_in_management") {
    document.getElementById("change_in_name_of_management").style.display = "block";
  }

}
document.getElementById("service_type").onchange = showFields;
// // selection field end
function submitForm1() {
  var form = document.getElementById("form1");
  var divValue = document.getElementById("noc_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit1
function submitForm2() {
  var form = document.getElementById("form2");
  var divValue = document.getElementById("sublease_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit2
function submitForm3() {
  var form = document.getElementById("form3");
  var divValue = document.getElementById("transfer_tags").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit3
function submitForm4() {
  var form = document.getElementById("form4");
  var divValue = document.getElementById("eb_poll_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit4
function submitForm5() {
  var form = document.getElementById("form5");
  var divValue = document.getElementById("water_requirment_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit5
function submitForm6() {
  var form = document.getElementById("form6");
  var divValue = document.getElementById("surrender_approval_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit6
function submitForm7() {
  var form = document.getElementById("form7");
  var divValue = document.getElementById("change_name_company_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit7
function submitForm8() {
  var form = document.getElementById("form8");
  var divValue = document.getElementById("reach_md_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit8
function submitForm9() {
  var form = document.getElementById("form9");
  var divValue = document.getElementById("other_services_details").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}

//submit9
function submitForm10() {
  var form = document.getElementById("form10");
  var divValue = document.getElementById("change_in_name_of_product").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit10
function submitForm11() {
  var form = document.getElementById("form11");
  var divValue = document.getElementById("change_in_name_of_constitution").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit11
function submitForm12() {
  var form = document.getElementById("form12");
  var divValue = document.getElementById("change_in_name_of_management").value;
  form.action = "/create/service?divValue=" + divValue;
  form.submit();
}
// submit12

// const table = document.getElementById('credit_table');
// const rows = table.querySelectorAll('tr[id^="7_"]');

// // Add onchange event to the last td in each row
// rows.forEach((row, index) => {
//   const lastCellInput = row.querySelector('td:last-child input.form-control');

//   lastCellInput.addEventListener('change', () => {
//     // Enable the next row if the last input field in the current row has a value
//     if (lastCellInput.value !== '') {
//       enableNextRowForCreditTable(index);
//     }
//   });
// });

// // Function to enable the next row in the credit table
// function onSanctionLetterChange(index) {
//   enableNextRowForCreditTable(index);
// }

// function enableNextRowForCreditTable(index) {
//   let currentRow = document.getElementById(`7_${index}`);
//   let nextRow = document.getElementById(`7_${index + 1}`);
//   let inputs = nextRow.getElementsByTagName('input');

//   for (let i = 0; i < inputs.length; i++) {
//     inputs[i].disabled = false;
//   }
// }
// // credit table

// function enableNextRow(rowNum) {
//   var nextRowNum = rowNum + 1;
//   document.getElementById('transfer_s_no_' + nextRowNum).disabled = false;
//   document.getElementById('date_year_approval_' + nextRowNum).disabled = false;
//   document.getElementById('name_of_transfer_unit_' + nextRowNum).disabled = false;
//   document.getElementById('transfer_plot_no_extent_' + nextRowNum).disabled = false;
//   document.getElementById('transfer_approve_products_' + nextRowNum).disabled = false;
//   document.getElementById('differential_plot_cost_demanded_' + nextRowNum).disabled = false;
//   document.getElementById('date_of_differential_cost_remitted_' + nextRowNum).disabled = false;
// }
// //transfer table
// function noc_earlier_select(){
//   var e = document.getElementById("noc_earlier_issued").value;
//   if(e == "yes"){
//       document.getElementById("noc_earlier_bank").style.display = "block";
//   }
//   else{
//       document.getElementById("noc_earlier_bank").style.display = "none";
      
//   }
// }
// noc_earlier_select();
// // yes no function fro noc earlier
// function whether_build_selection(){
//   var g = document.getElementById("whether_built_up_area").value;
//   if(g == "yes"){
//       document.getElementById("whether_sublease").style.display = "block";
//   }
//   else{
//       document.getElementById("whether_sublease").style.display = "none";
      
//   }
// }
// whether_build_selection();
// // whether obtained
// function whether_modified_selection() {
//   var selectElement = document.getElementById("whether_modified_lease");
//   var selectedOption = selectElement.value;

//   var mldDiv = document.getElementById("mld_document_display");
//   var documentDiv = document.getElementById("reason_mld");

//   if (selectedOption === "yes") {
//       mldDiv.style.display = "block";
//       documentDiv.style.display = "none";
//   } else if (selectedOption === "no") {
//       mldDiv.style.display = "none";
//       documentDiv.style.display = "block";
//   }
//   else{
//     mldDiv.style.display = "none";
//       documentDiv.style.display = "none";
//   }
// }
// // whether_modified yes no
// function whether_noc_selection() {
//   var selectElement = document.getElementById("whether_noc_sipcot");
//   var selectedOption = selectElement.value;

//   var mldDive = document.getElementById("whether_no_due_display");
//   var documentDive = document.getElementById("sub_leased_third");

//   if (selectedOption === "yes") {
//       mldDive.style.display = "block";
//       documentDive.style.display = "none";
//   } else if (selectedOption === "no") {
//       mldDive.style.display = "none";
//       documentDive.style.display = "block";
//   }
//   else{
//     mldDive.style.display = "none";
//       documentDive.style.display = "none";
//   }
// }
// // whether_noc_selection
// function functioning_status_selection() {
//   var selectElements = document.getElementById("functioning_status");
//   var selectedOptions = selectElements.value;

//   var mldDiven = document.getElementById("no_years_functioning_display");
//   var documentDiven = document.getElementById("transfer_effeted_display");

//   if (selectedOptions === "yes") {
//       mldDiven.style.display = "block";
//       documentDiven.style.display = "none";
//   } else if (selectedOptions === "no") {
//       mldDiven.style.display = "none";
//       documentDiven.style.display = "block";
//   }
//   else{
//     mldDiven.style.display = "none";
//       documentDiven.style.display = "none";
//   }
// }
// // functioning_status_selection
// function eb_corridor_selection(){
//   var g = document.getElementById("eb_corridor").value;
//   if(g === "no"){
//      alert("You Are Not Eligible");
//   }
  
// }
// eb_corridor_selection();
// // eb_corridor_selection
// function eb_poll_inside_selection(){
//   var h = document.getElementById("eb_poll_inside_plot").value;
//   if(h === "yes"){
//       document.getElementById("types_of_polls_display").style.display = "block";
//   }
//   else{
//       document.getElementById("types_of_polls_display").style.display = "none";
      
//   }
// }
// eb_poll_inside_selection();
// eb poll
function isAlphabetic(event) {
  var charCode = event.which || event.keyCode;
  
  // Exclude space (32) and period (46)
  if (
    (charCode >= 65 && charCode <= 90) || // Uppercase letters
    (charCode >= 97 && charCode <= 122) || // Lowercase letters
    charCode === 46 || // Period (.)
    charCode === 32 // Space
  ) {
    return true; // Allow the character
  } else {
    return false; // Block the character
  }
}


//Name Validation

function isNumberKey(evt) {
  var charCode = (evt.which) ? evt.which : event12.keyCode;
  var charStr = String.fromCharCode(charCode);
  if (charStr == '+' || charStr == '-' || (charStr >= '0' && charStr <= '9')) {
    return true;
  } else {
    return false;
  }
}
//Phone number
function isNumberKeydec(evt) {
  var charCode = (evt.which) ? evt.which : event1.keyCode;
  var charStr = String.fromCharCode(charCode);
  if (charStr == '.' || (charStr >= '0' && charStr <= '9')) {
    return true;
  } else {
    return false;
  }
}
// decimal number
function isNumberKeyamount(evt) {
  var charCode = (evt.which) ? evt.which : event2.keyCode;
  var charStr = String.fromCharCode(charCode);
  if (charStr == ',' || (charStr >= '0' && charStr <= '9')) {
    return true;
  } else {
    return false;
  }
}
// amount validation
function validateInput(event) {
  var key = event.which ? event.which : event.keyCode;
  if (key >= 48 && key <= 57) {
    return true;
  } else {
    event.preventDefault();
    return false;
  }
}
//Pincode validation & number only validation
function limitTextarea(element, maxLength) {
  if (element.value.length > maxLength) {
    element.value = element.value.substr(0, maxLength);
  }
}
// text area
function surrender_approval_selection(){
  var select = document.getElementById("surrender_approval_type_of_water").value;
  if(select === 'surrender_partially'){
    document.getElementById("total_extend").style.display="block"
  }else{
    document.getElementById("total_extend").style.display="none";
  }
}
surrender_approval_selection()
function _openDemo() {
  var e = document.getElementById("pole_plot").value;
  if (e == "yes") {
    document.getElementById("demo_1").style.display = "block";
    document.getElementById("demo_2").style.display = "none";
  } else if (e == "no") {
    document.getElementById("demo_1").style.display = "none";
    document.getElementById("demo_2").style.display = "block";
  }
}