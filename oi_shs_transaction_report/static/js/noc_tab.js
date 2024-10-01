

function activateTab(tabId) {
  // Hide all tabs
  var tabs = document.getElementsByClassName("tab-pane");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].style.display = "none";
  }

  // Show the specified tab
  var tab = document.querySelector(tabId);
  tab.style.display = "block";

  // Update the active tab in the navigation
  var navLinks = document.getElementsByClassName("nav-link");
  for (var j = 0; j < navLinks.length; j++) {
    navLinks[j].classList.remove("active");
  }

  var activeNavLink = document.querySelector('a[data-target="' + tabId + '"]');
  activeNavLink.classList.add("active");
}

function validateTab1() {
  var noc_name = document.getElementById("name");
  var mobile_number = document.getElementById("mobile");
  var noc_email = document.getElementById("email");
  // ... validate other fields for tab1

  if (noc_name.value === "" || mobile_number.value === "") {
    alert("Please fill all Mandatory Data's ");
    return false;
  } else {
    activateTab("#tab2Content");
    return true;
  }
}

function validateTab2() {
  var credit_name = document.getElementById("credit_name1");
  var credit_bank_name = document.getElementById("credit_bank_name1");
  // ... validate other fields for tab2

  if (credit_name.value === "" ) {
    alert("Please fill all Mandatory Data's");
    return false;
  } else {
    activateTab("#tab3Content");
    return true;
  }
}

function goBackToTab2() {
  activateTab("#tab2Content");
}