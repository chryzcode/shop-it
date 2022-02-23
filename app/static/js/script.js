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

//CAROUSEL

//declear variables
const track = document.querySelector(".carousel__track");
// an array of all the slides
const slides = Array.from(track.children);
const nextButton = document.querySelector(".carousel__button--right");
const prevButton = document.querySelector(".carousel__button--left");
const dotsNav = document.querySelector(".carousel__nav");
// an array of all the dots
const dots = Array.from(dotsNav.children);
//get the width of the first slide
const slideWidth = slides[0].getBoundingClientRect().width;

// a function that gets the width of a slide and multiplies it by the index of the slide to get the left position
const setSlidePosition = (slide, index) => {
  slide.style.left = slideWidth * index + "px";
};

//apply the setSlidePosition for each of the slides
slides.forEach(setSlidePosition);

const moveToSlide = (track, currentSlide, targetSlide) => {
  //move the next slide
  track.style.transform = "translateX(-" + targetSlide.style.left + ")";

  //dynamically changing the current slide
  currentSlide.classList.remove("currentSlide");
  targetSlide.classList.add("currentSlide");
};

const updateDots = (currentDot, targetDot) => {
  //remove the current dot class property
  currentDot.classList.remove("current-slide");
  //add the current dot class property
  targetDot.classList.add("current-slide");
};

const hideShowArrows = (slides, prevButton, nextButton, targetIndex) => {
  if (targetIndex === 0) {
    prevButton.classList.add("is-hidden");
    nextButton.classList.remove("is-hidden");
  } else if (targetIndex === slides.length - 1) {
    prevButton.classList.remove("is-hidden");
    nextButton.classList.add("is-hidden");
  } else {
    prevButton.classList.remove("is-hidden");
    nextButton.classList.remove("is-hidden");
  }
};

prevButton.addEventListener("click", e => {
  //get current slide through the track
  const currentSlide = track.querySelector(".currentSlide");
  //get the current slide
  const prevSlide = currentSlide.previousElementSibling;
  //get the space for moving tot the next slide

  const currentDot = dotsNav.querySelector(".current-slide");
  const prevDot = currentDot.previousElementSibling;
  const prevIndex = slides.findIndex(slide => slide === prevSlide);

  moveToSlide(track, currentSlide, prevSlide);
  updateDots(currentDot, prevDot);
  hideShowArrows(slides, prevButton, nextButton, prevIndex);
});

nextButton.addEventListener("click", e => {
  //get current slide through the track
  const currentSlide = track.querySelector(".currentSlide");
  //get the current slide
  const nextSlide = currentSlide.nextElementSibling;
  //get the space for moving tot the next slide

  const currentDot = dotsNav.querySelector(".current-slide");
  const nextDot = currentDot.nextElementSibling;
  const nextIndex = slides.findIndex(slide => slide === nextSlide);

  moveToSlide(track, currentSlide, nextSlide);
  updateDots(currentDot, nextDot);
  hideShowArrows(slides, prevButton, nextButton, nextIndex);
});

dotsNav.addEventListener("click", e => {
  //get the nav dot
  const targetDot = e.target.closest("button");
  // if not the nav dot stop the function
  if (!targetDot) return;

  //get the current slide
  const currentSlide = track.querySelector(".currentSlide");
  //get the current dot
  const currentDot = dotsNav.querySelector(".current-slide");
  //get the index of the target dot
  const targetIndex = dots.findIndex(dot => dot === targetDot);
  //get the target slide
  const targetSlide = slides[targetIndex];

  moveToSlide(track, currentSlide, targetSlide);
  updateDots(currentDot, targetDot);
  hideShowArrows(slides, prevButton, nextButton, targetIndex);
});
