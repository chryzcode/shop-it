const navbar = document.getElementsByTagName("nav");
const toogle = document.getElementById("toogle");
const nav_links = document.getElementById("nav-links");
const store_side_nav = document.getElementById("store-sidenav");
console.log(store_side_nav);


document.onclick = function (e) {
  if (e.target.id == "a-nav-link") {
    nav_links.classList.remove("active");
    toogle.classList.remove("active");
    store_side_nav.classList.remove("active");
  }
};

toogle.onclick = function () {
  toogle.classList.toggle("active");
  // nav_links.classList.toggle("active");
  store_side_nav.classList.toggle("active");
};








