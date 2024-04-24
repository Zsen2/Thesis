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
  console.log("check() function called");
  const radioButtons = document.querySelectorAll('input[name="fruit"]');
  let isChecked = false;

  radioButtons.forEach((button) => {
    if (button.checked) {
      isChecked = true;
      // Get the value of the selected fruit
      const selectedFruit = button.value;
      // Set the value of the hidden input field
      document.getElementById("selected_fruit").value = selectedFruit;
      console.log("Selected fruit:", selectedFruit); // Debugging statement
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
