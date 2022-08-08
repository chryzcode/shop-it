const navbar = document.getElementById("nav");
const toogle = document.getElementById("toogle");
const nav_links = document.getElementById("nav-links");
const store_side_nav = document.getElementById("store-sidenav");
const profile_dropdown = document.getElementById("acc-store-nav-links");
const profile_section = document.getElementById("nav-user-profile");
const profile_icon = document.getElementById("profile-icon");
const notification = document.getElementById("notification");
const notification_dropdown = document.getElementById("notification-dropdown");
const search_bar = document.getElementById("side-nav-search-bar");
const search_display = document.getElementById("search-display");
const analytics_timeline_toogle = document.getElementById("analtics-timeline-toogle");
const monthly_yearly_analytics = document.getElementById("small-anlytics-card-monthly-yearly");
const hourly_weekly_analytics = document.getElementById("small-anlytics-card-hourly-weekly");
const mobile_search_bar = document.getElementById("side-nav-search-bar-mobile");
const mobile_search_display = document.getElementById("search-display-mobile");
const searchMediaQuery = window.matchMedia("(min-width: 990px)");
const customerNav = document.getElementById("side-nav-search-bar-customer");
const withdrawNairaBtn = document.getElementById("withdraw-naira-btn");
const nairaWalletPopOut = document.getElementById("withdrawal-naira-form");


if (withdrawNairaBtn) {
  withdrawNairaBtn.onclick = function (e) {
    if (e.target.id == "withdraw-naira-btn") {
      nairaWalletPopOut.classList.add("active");
    }
   
  }
}


document.onclick = function (e) {
  if (e.target.id == "a-nav-link") {
    nav_links.classList.remove("active");
    toogle.classList.remove("active");
  }
  if (nairaWalletPopOut) {
    if (e.target.id != "withdraw-naira-btn") {
      nairaWalletPopOut.classList.remove("active");
    }
  }
  if (store_side_nav) {
    if (e.target.id == "nav") {
      store_side_nav.classList.remove("active");
      toogle.classList.remove("active");
    }
  }

};

toogle.onclick = function () {
  toogle.classList.toggle("active");
  if (nav_links) {
    nav_links.classList.toggle("active");
    nav.classList.toggle("active");
  }
  if (store_side_nav) {
    store_side_nav.classList.toggle("active");
  }
};

if (profile_section) {
  profile_section.onclick = function () {
    if (profile_dropdown) {
      profile_dropdown.classList.toggle("active");
      profile_icon.classList.toggle("active");
      if (profile_dropdown.classList.contains("active")) {
        navbar.style.overflow = "visible";
      }
    }
  };
}


if (notification) {
  notification.onclick = function () {
    notification_dropdown.classList.toggle("active");
    notification.classList.toggle("active");
    if (notification_dropdown.classList.contains("active")) {
      navbar.style.overflow = "visible";
    }
  };
}



if (analytics_timeline_toogle) {
  analytics_timeline_toogle.onclick = function () {
    monthly_yearly_analytics.classList.toggle("active");
    hourly_weekly_analytics.classList.toggle("inactive");
  };
}

function desktopSearchBar() {
  if (search_bar) {
    document.onclick = function (e) {
      if (search_display) {
        if (e.target.id != "side-nav-search-bar") {
          search_display.classList.remove("active");
        } else {
          search_display.classList.add("active");
        }
      }
    };
  }
}

function customerSearchBar() {
  if (customerNav) {
    document.onclick = function (e) {
      if (search_display) {
        if (e.target.id != "side-nav-search-bar-customer") {
          search_display.classList.remove("active");
        } else {
          search_display.classList.add("active");
        }
      }
    };
  }
}

function storeMobileSearchBar() {
  if (mobile_search_bar) {
    document.onclick = function (e) {
      if (mobile_search_display) {
        if (e.target.id != "side-nav-search-bar-mobile") {
          mobile_search_display.classList.remove("active");
        } else {
          mobile_search_display.classList.add("active");
        }
      }
    };
  }
}

function myFunction() {
  var input, filter, ul, li, a, i, txtValue;
  if (search_bar) {
    input = document.getElementById("side-nav-search-bar");
  } else if (customerNav) {
    input = document.getElementById("side-nav-search-bar-customer");
  }
  if (searchMediaQuery.matches) {
    if (search_bar) {
      input = document.getElementById("side-nav-search-bar");
    } else if (customerNav) {
      input = document.getElementById("side-nav-search-bar-customer");
    }
    ul = document.getElementById("search-display");
    console.log(input);
  } else if (mobile_search_display) {
    if (mobile_search_bar) {
      input = document.getElementById("side-nav-search-bar-mobile");
    }

    ul = document.getElementById("search-display-mobile");
    console.log(input);
  } else {
    if (search_bar) {
      input = document.getElementById("side-nav-search-bar");
    } else if (customerNav) {
      input = document.getElementById("side-nav-search-bar-customer");
    }
    ul = document.getElementById("search-display");
  }
  filter = input.value.toUpperCase();

  li = ul.getElementsByTagName("li");

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
  ul.style.height = "auto";
}
