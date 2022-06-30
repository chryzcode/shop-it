const navbar = document.getElementById("nav");
const toogle = document.getElementById("toogle");
const nav_links = document.getElementById("nav-links");
const store_side_nav = document.getElementById("store-sidenav");
const profile_dropdown = document.getElementById("acc-store-nav-links");
const profile_section = document.getElementById("nav-user-profile")
const profile_icon = document.getElementById("profile-icon");
const notification = document.getElementById("notification");
const notification_dropdown = document.getElementById("notification-dropdown");


document.onclick = function (e) {
  if (e.target.id == "a-nav-link") {
    nav_links.classList.remove("active");
    toogle.classList.remove("active");
  }
};

toogle.onclick = function () {
  toogle.classList.toggle("active");
  if (nav_links) {
    nav_links.classList.toggle("active");
  }
  if (store_side_nav) {
    store_side_nav.classList.toggle("active");
  }
};

profile_section.onclick = function () {
  if (profile_dropdown) {
    profile_dropdown.classList.toggle("active");
    profile_icon.classList.toggle("active");
  }
};

document.onclick = function (e) {
  if (profile_dropdown) {
    if (
      e.target.classList == "store-products-container" ||
      e.target.classList == "subscription-grid-container"
    ) {
      profile_dropdown.classList.remove("active");
      profile_icon.classList.remove("active");
    }
  }

  if (store_side_nav) {
    if (e.target.id == "nav") {
      store_side_nav.classList.remove("active");
      toogle.classList.remove("active");
    }
  }
};

console.log(notification)

if (notification) {
  notification.onclick = function () {
    notification_dropdown.classList.toggle("active");
  }
}



// document.onclick = function (e) {
//   if (e.target.id == profile_section) {
//     profile_dropdown.classList.remove("active");
//   }
//   if (e.target.id == navbar) {
//     store_side_nav.classList.remove("active");
//   }
// };
















