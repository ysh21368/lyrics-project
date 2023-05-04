
var modal = document.getElementById("myModal");
var textarea = document.getElementById("myTextarea");
var spinner = document.getElementById("spinner");

function openModal() {
  document.getElementById("myModal").style.display = "block";
  spinner.style.display = "none";
}


$('#submit').click(function(){
  var textarea = document.getElementById("myTextarea");
  if (textarea.value == ''){
    alert('가사를 입력해 주세요.')
    textarea.focus()
    return false;
  }
  // spinner.show();
  showModal();
  return true;
    });

$("#category").change(function () {
  var category = $("#category option:checked").text()
  if (category == '가사' || category== '가수'){
    $("#search").attr("placeholder", category+"를 입력하세요");
  }else{

    $("#search").attr("placeholder", category+"을 입력하세요");
  }
});

function showModal() {
  modal.style.display = "block";
  textarea.setAttribute("readonly", true);
  spinner.style.display = "block";
}

function hideModal() {
  modal.style.display = "none";
  textarea.removeAttribute("readonly");
  spinner.style.display = "none";
}
function closeModal() {
  hideModal();
}
document.addEventListener("keydown", function(event) {
  // Check if "esc" key was pressed (key code 27)
  if (event.keyCode === 27) {
    // Call closeModal() function to close the modal
    closeModal();
  }
});
function resetTextarea() {
  var textarea = document.getElementById("myTextarea");
  textarea.value = "";
}

