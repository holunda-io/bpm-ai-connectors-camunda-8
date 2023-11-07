
disable_animations = """
    *, *::before, *::after { 
        animation-duration: 0s !important; 
        transition-duration: 0s !important; 
    }
"""

ripple_css = """
    .web-agent-ripple {
      position: absolute;
      border-radius: 50%;
      transform: scale(0);
      animation: web-agent-ripple 0.5s ease-out;
      background-color: rgba(244, 67, 54, 0.961);
      pointer-events: none;
      z-index: 9999;
    }

    @keyframes web-agent-ripple {
      to {
        transform: scale(3);
        opacity: 0;
      }
    }
"""

ripple_js = """
    document.body.addEventListener('click', function(event) {
        const y = event.pageY - 10;
        const x = event.pageX - 10;
                
        const rippleRadius = 20;
        const ripple = document.createElement('div');
        ripple.classList.add('web-agent-ripple');
        
        ripple.style.width = ripple.style.height = `${rippleRadius * 2}px`;
        ripple.style.top = `${y - rippleRadius}px`;
        ripple.style.left = `${x - rippleRadius}px`;

        // Append the effect to the body and remove it after the animation completes
        document.body.appendChild(ripple);
        setTimeout(() => {
            document.body.removeChild(ripple);
        }, 500);
    }, true);
"""
