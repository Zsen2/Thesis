function openPopup() {
  document.querySelector(".pop-up-overlay").classList.add("active");
}

function closePopup() {
  document.querySelector(".pop-up-overlay").classList.remove("active");
}

function handleOverlayClick(event) {
  if (event.target.classList.contains("pop-up-overlay")) {
    closePopup();
  }
}

function check() {
  const radioButtons = document.querySelectorAll('input[name="fruit"]');
  let isChecked = false;

  radioButtons.forEach((button) => {
    if (button.checked) {
      isChecked = true;
    }
  });

  if (!isChecked) {
    document.getElementById("error-message").style.display = "block";
    return false;
  } else {
    document.getElementById("error-message").style.display = "none";
    closePopup();
    return true;
  }
}

document
  .querySelector(".pop-up-overlay")
  .addEventListener("click", handleOverlayClick);
