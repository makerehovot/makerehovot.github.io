// Click a gallery photo to view it larger.
(function () {
  const box = document.getElementById("lightbox");
  if (!box) return;
  const big = box.querySelector("img");
  document.querySelectorAll(".gallery .shot").forEach((b) => {
    b.addEventListener("click", () => {
      const img = b.querySelector("img");
      big.src = img.src;
      big.alt = img.alt;
      box.showModal();
    });
  });
  // close on the X button or by clicking outside the photo
  box.addEventListener("click", (e) => { if (e.target !== big) box.close(); });
})();
