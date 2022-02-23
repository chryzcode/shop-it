const navbar = document.getElementsByTagName("nav");
const toogle = document.getElementById("toogle");
const nav_links = document.getElementById("nav-links");

document.onclick = function (e) {
  if (e.target.id == "a-nav-link") {
    nav_links.classList.remove("active");
    toogle.classList.remove("active");
  }
};

toogle.onclick = function () {
  toogle.classList.toggle("active");
  nav_links.classList.toggle("active");
};

