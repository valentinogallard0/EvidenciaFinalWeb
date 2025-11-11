(function () {
  const links = document.querySelectorAll(".panel-link");
  const body = document.body;

  function showLoaderAndNavigate(href) {
    if (!href) {
      return;
    }
    body.classList.add("is-loading");
    setTimeout(() => {
      window.location.href = href;
    }, 180);
  }

  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      if (link.classList.contains("active")) {
        return;
      }
      event.preventDefault();
      showLoaderAndNavigate(link.getAttribute("href"));
    });
  });

  window.addEventListener("pageshow", () => {
    body.classList.remove("is-loading");
  });
})();
