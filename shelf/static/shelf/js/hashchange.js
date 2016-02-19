var shiftWindow = function() {
  scrollBy(0, -95);
  console.log('scroll');
};
if (location.hash) shiftWindow();
window.addEventListener("hashchange", shiftWindow);