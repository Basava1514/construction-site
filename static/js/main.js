document.addEventListener('DOMContentLoaded', function(){
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', function(e){
      e.preventDefault(); document.querySelector(this.getAttribute('href'))?.scrollIntoView({behavior:'smooth'});
    });
  });
});
