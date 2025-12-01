document.addEventListener("DOMContentLoaded", function () {
  // Modal Logic
  const modal = document.getElementById("contact-modal");
  const btn = document.querySelector(".nav-link");
  const span = document.getElementsByClassName("close-button")[0];

  if (btn && modal && span) {
    btn.onclick = function (e) {
      e.preventDefault();
      modal.style.display = "flex";
    };

    span.onclick = function () {
      modal.style.display = "none";
    };

    window.onclick = function (event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    };
  }

  // Auto-refresh map every 60 seconds
  setInterval(function () {
    const mapFrame = document.getElementById("map-frame");
    if (mapFrame) {
      mapFrame.src = mapFrame.src;
    }
  }, 30000);
});
