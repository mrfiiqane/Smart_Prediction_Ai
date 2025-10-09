const faqs = document.querySelectorAll(".faq-group-header");
  faqs.forEach(header => {
    header.addEventListener("click", () => {
      const body = header.nextElementSibling;
      const icon = header.querySelector("i");
      body.classList.toggle("open");
      icon.classList.toggle("fa-plus");
      icon.classList.toggle("fa-minus");
    });
  });