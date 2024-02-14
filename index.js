document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    // Assuming 'open' class changes the ball to an "opened" state visually
    document.getElementById('soccerBall').classList.add('open');

    // Reveal the welcome message after the ball "opens"
    setTimeout(function() {
      document.getElementById('welcomeMessage').style.opacity = 1;
    }, 1000); // Adjust timing based on your "opening" animation
  }, 3000); // This should match the duration of the initial spin and zoom
});

