"""
Layout component for Arca - provides the base HTML structure for all pages
with a design inspired by classic Windows 98
"""

class Layout:
    """
    Base layout component for all pages
    Provides the HTML structure, CSS, and navigation
    Embracing the Windows 98 aesthetic
    """
    
    def render(self, children=None):
        """
        Render the layout with the provided children
        
        Args:
            children: The content to render inside the layout
            
        Returns:
            str: The rendered HTML
        """
        # No Tailwind config needed - we're going full Windows 98 style
        custom_styles = r"""
            /* Windows 98 Color Palette - Updated according to design system */
            :root {
                --win98-gray: #c0c0c0;
                --win98-dark-gray: #808080;
                --win98-darker-gray: #404040;
                --win98-light-gray: #dfdfdf;
                --win98-black: #000000;
                --win98-white: #ffffff;
                --win98-blue: #0000ff;
                --win98-dark-blue: #000080;
                --win98-cyan: #00ffff;
                --win98-red: #ff0000;
                --win98-yellow: #ffff00;
                --win98-green: #00ff00;
                --win98-magenta: #ff00ff;
                
                /* Gradients and special effects */
                --title-bar-gradient: linear-gradient(90deg, #000080, #1084d0);
                --menu-gradient: linear-gradient(to bottom, #fff, #ece9d8);
                --button-face: var(--win98-gray);
                --button-highlight: var(--win98-white);
                --button-shadow: var(--win98-dark-gray);
            }
            
            body {
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                background-color: var(--win98-gray);
                margin: 0;
                padding: 0;
                color: var(--win98-black);
                overflow: hidden;
                height: 100vh;
                /* Disable font smoothing for pixel-perfect rendering */
                -webkit-font-smoothing: none;
                -moz-osx-font-smoothing: grayscale;
                font-size: 12px;
            }
            
            /* Modern scrollbar with Windows 98 colors */
            ::-webkit-scrollbar {
                width: 16px;
                height: 16px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--win98-gray);
                border-left: 1px solid var(--win98-white);
                border-top: 1px solid var(--win98-white);
                border-right: 1px solid var(--win98-dark-gray);
                border-bottom: 1px solid var(--win98-dark-gray);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--win98-gray);
                border-left: 1px solid var(--win98-white);
                border-top: 1px solid var(--win98-white);
                border-right: 1px solid var(--win98-dark-gray);
                border-bottom: 1px solid var(--win98-dark-gray);
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--win98-light-gray);
            }
            
            /* Windows 98 Panel */
            .win98-panel {
                background-color: var(--win98-gray);
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 2px 2px 0 var(--win98-white) inset, -2px -2px 0 var(--win98-dark-gray) inset;
            }
            
            .win98-panel-inset {
                background-color: var(--win98-white);
                border: 2px inset var(--win98-gray);
            }
            
            /* Windows 98 Window */
            .win98-window {
                background-color: var(--win98-gray);
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 1px 1px 0 var(--win98-dark-gray) inset, -1px -1px 0 var(--win98-white) inset;
                margin-bottom: 10px;
            }
            
            .win98-window-title {
                background-image: var(--title-bar-gradient);
                padding: 2px 3px;
                color: var(--win98-white);
                font-weight: bold;
                font-size: 11px;
                display: flex;
                justify-content: space-between;
            }
            
            /* Windows 98 Button */
            .win98-btn {
                font-family: 'MS Sans Serif', 'Segoe UI', Tahoma, sans-serif;
                background-color: var(--button-face);
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 1px 1px 0 var(--win98-dark-gray) inset, -1px -1px 0 var(--win98-white) inset;
                padding: 4px 10px;
                font-size: 12px;
                color: var(--win98-black);
                cursor: pointer;
                outline: none;
                margin-right: 5px;
            }
            
            .win98-btn:active {
                border-color: var(--win98-black) var(--win98-white) var(--win98-white) var(--win98-black);
                box-shadow: 1px 1px 0 var(--win98-white) inset, -1px -1px 0 var(--win98-dark-gray) inset;
                padding: 5px 9px 3px 11px;
            }
            
            .win98-btn:focus {
                outline: 1px dotted black;
                outline-offset: -5px;
            }
            
            /* Windows 98 Tables */
            .win98-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                font-size: 12px;
                color: var(--win98-black);
            }
            
            .win98-table-header {
                background-color: var(--win98-gray);
                font-weight: bold;
            }
            
            .win98-table-header th {
                padding: 4px 8px;
                text-align: left;
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
            }
            
            .win98-table-cell {
                padding: 4px 8px;
                border-bottom: 1px solid var(--win98-dark-gray);
                border-right: 1px solid var(--win98-dark-gray);
            }
            
            .win98-table-row:hover {
                background-color: var(--win98-light-gray);
            }
            
            .win98-table-row-alt {
                background-color: #f0f0f0;
            }
            
            .win98-table-row-alt:hover {
                background-color: var(--win98-light-gray);
            }
            
            /* Text alignment utilities */
            .text-left { text-align: left; }
            .text-center { text-align: center; }
            .text-right { text-align: right; }
            
            /* Icon button */
            .win98-icon-btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                background-color: var(--button-face);
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 1px 1px 0 var(--win98-dark-gray) inset, -1px -1px 0 var(--win98-white) inset;
                padding: 2px;
                margin: 0 2px;
                cursor: pointer;
            }
            
            .win98-icon-btn:active {
                border-color: var(--win98-black) var(--win98-white) var(--win98-white) var(--win98-black);
                box-shadow: 1px 1px 0 var(--win98-white) inset, -1px -1px 0 var(--win98-dark-gray) inset;
                padding: 3px 1px 1px 3px;
            }
            
            /* Icons */
            .las {
                color: var(--win98-black);
                -webkit-font-smoothing: none;
                -moz-osx-font-smoothing: grayscale;
                font-size: 16px;
            }
            
            .las.disabled {
                color: var(--win98-dark-gray);
            }
            
            /* Standard icon sizes */
            .la-sm { font-size: 12px; }
            .la-md { font-size: 16px; }
            .la-lg { font-size: 24px; }
            
            /* Win98 styled icons */
            .win98-icon {
                image-rendering: pixelated;
                text-shadow: 0.5px 0 0 var(--win98-dark-gray), 0 0.5px 0 var(--win98-dark-gray);
            }
            
            .win98-icon.primary { color: var(--win98-dark-blue); }
            .win98-icon.destructive { color: var(--win98-red); }
            .win98-icon.success { color: var(--win98-green); }
            
            /* Button flicker effect */
            .btn-flicker {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                opacity: 0;
                pointer-events: none;
            }
            
            @keyframes btn-flicker {
                0% { opacity: 0; left: -100%; }
                30% { opacity: 0.5; }
                100% { opacity: 0; left: 100%; }
            }
            
            /* Table style with zebra striping */
            .win98-table {
                border-collapse: collapse;
                width: 100%;
                border: 1px solid var(--win98-dark-gray);
            }
            
            .win98-table th {
                background-color: var(--win98-gray);
                border: 1px solid var(--win98-dark-gray);
                padding: 4px 8px;
                text-align: left;
                font-weight: bold;
                position: relative;
            }
            
            .win98-table th:after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
            }
            
            .win98-table td {
                border: 1px solid var(--win98-dark-gray);
                padding: 4px 8px;
            }
            
            .win98-table tr.even {
                background-color: white;
            }
            
            .win98-table tr.odd {
                background-color: #f0f0f0;
            }
            
            .win98-table tr:hover {
                background-color: rgba(0, 178, 255, 0.1);
            }
            
            /* Form controls */
            .win98-input {
                background-color: white;
                border-top: 2px solid var(--win98-dark-gray);
                border-left: 2px solid var(--win98-dark-gray);
                border-right: 2px solid white;
                border-bottom: 2px solid white;
                padding: 4px;
                font-family: "MS Sans Serif", Arial, sans-serif;
                font-size: 12px;
                outline: none;
                transition: box-shadow 0.2s ease;
            }
            
            .win98-input:focus {
                box-shadow: 0 0 10px rgba(0, 178, 255, 0.4);
            }
            
            /* Icons */
            .win98-icon {
                width: 16px;
                height: 16px;
                margin-right: 4px;
            }
            
            /* Main desktop layout */
            .desktop {
                height: 100vh;
                display: flex;
                flex-direction: column;
                background-color: #008080;
                background-image: linear-gradient(135deg, rgba(0, 139, 139, 0.4), rgba(0, 80, 120, 0.6)), 
                                  url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOeSURBVGhD7ZlbSBRRGMf/u+qmZWlaaiHdwLrQjWirh4gegl6ksh6KHoKgh+op6K2XqKegh4pIoqALIdVDBUGJ2J1ulBWtXexCmi2WbZYtbY6/M86ss+vOzM6scfTA/mD3nDPf+c75z5nv3BYMU/Qvc+Enmf/juCw9I1xXV4exsTGkpKQgLS0Nc3NzWFlZedAh5IQicmZ6OlPb+/q40SFB39gb+/v7MTIygqKiIuTl5SEzM5PLbWVlJdNtbW2wWCzQ6XSw2WzweDzMNj4+ztqoTUtLC2ZmZlje5ORkvrmD4jE2mJycZG2zs7Osbnx2ds5UVFTwFHs8n3F4eJglxvPlxvUZDWZEXn3/gSc1tdgIhdi1JPb29kJv0CNoDcGfpVOkUAE09+lxfb0aSVoNvjRbYSs/zbW+I/pM9GjhQm/7G/h9fu7lDNPT07BYLP/8ZHcEMuUo10Lx+fWItyFhiUikKxLjb7p5LDJxEdnY2Ijo8QXCPBYZVUVCoRCqqqpY+eTJU1YeHh62o+nRI1YuLCy0K/t8Pni9XtYn2DFHIhFm14IW3kNHjo6OkJOTw8qOOe3w+dBnrof3bhX0+kQYjcl4WF2N/tVVbDa/gOdmJbaSkxNk+vv6OCrASsVFu3/4/bUcb293CcrwnQmEJyZ4KjxqJ74/e47ItWscSTL/zkjbVlR0Mh6YnMNuuzhfVIbavgEZwv9XRH6+q7cTrBRtXeF/+iVNJJV3I/YC0TVLscTyiMaIUVJEEu/dDYvYkkTokxhREUUTMdIH06lOYFMH6G6s0y/m2LWYbpMZR9u8nHGRxNQRSqLF9gjJmZlwLX7hKDwRyZiGhoZgNpvZUZRs9N96HrndLZzcWXi9/t+uaRUlxPCk3H77jhuFiRggGI1GmEwmuzbqk5GRwfoxiPqoR10GlYOBACvbSk+hbX4By6ur2A8GeRt7TqnfYSAA/fAwjkXn9TbCi4soLi5m9xZ1IzMXGx8nMiShECPy5sEDtMR4M50UCp53dXWhtLT0ylhK2tvbYbVabV6vwMbGJrKzs2E2m/nkSRc8Ly8vvK6/vx9ut5tHIxMIBJCammqTnkuXNjdnqrxbxVPscdls4pssKXbPxOcj9J0VEQU/SFBEZP0gQU7kjzxI0BIi68MXHbQE+rBFI+xyuWAwGO48bpcrOEYcToK2DwKdUCm5nCgbOp2zzXLGgmPkMs9I0wE/yXB+AbcMEPhIiTanAAAAAElFTkSuQmCC');
                background-size: 100% 100%, 100px 100px;
                position: relative;
            }
            
            /* Taskbar */
            .taskbar {
                display: flex;
                background-color: var(--win98-gray);
                border-top: 2px solid white;
                height: 30px;
                width: 100%;
                z-index: 10;
            }
            
            /* Start button with neon effect */
            .start-button {
                display: flex;
                align-items: center;
                background-color: var(--win98-gray);
                border-top: 2px solid white;
                border-left: 2px solid white;
                border-right: 2px solid var(--win98-dark-gray);
                border-bottom: 2px solid var(--win98-dark-gray);
                padding: 2px 5px;
                margin: 2px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .start-button:before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, var(--neon-blue) 0%, transparent 70%);
                opacity: 0;
                transition: opacity 0.5s ease;
                pointer-events: none;
            }
            
            .start-button:hover:before {
                opacity: 0.15;
            }
            
            .start-button:active {
                border-top: 2px solid var(--win98-dark-gray);
                border-left: 2px solid var(--win98-dark-gray);
                border-right: 2px solid white;
                border-bottom: 2px solid white;
            }
            
            /* Start menu futuristic style */
            .start-menu {
                position: absolute;
                bottom: 30px;
                left: 0;
                background-color: var(--win98-gray);
                border: 2px solid;
                border-color: var(--win98-white) var(--win98-black) var(--win98-black) var(--win98-white);
                box-shadow: 1px 1px 0 var(--win98-dark-gray) inset, -1px -1px 0 var(--win98-white) inset;
                display: none;
                z-index: 100;
                min-width: 200px;
            }
            
            .start-menu-header {
                background-image: var(--title-bar-gradient);
                color: var(--win98-white);
                padding: 4px 8px;
                font-weight: bold;
                font-size: 11px;
                display: flex;
                align-items: center;
            }
            
            .start-menu-content {
                display: flex;
            }
            
            /* Desktop content */
            .desktop-content {
                flex: 1;
                padding: 10px;
                overflow: auto;
                position: relative;
            }
            
            /* Status bar with digital clock */
            .status-bar {
                display: flex;
                background-color: var(--win98-gray);
                border-top: 2px solid var(--win98-dark-gray);
                border-left: 1px solid var(--win98-dark-gray);
                height: 22px;
                padding: 2px 5px;
                font-size: 12px;
                align-items: center;
            }
            
            /* Digital clock with neon effect */
            #clock {
                font-family: "Digital", monospace;
                background-color: var(--win98-gray);
                color: black;
                padding: 0 5px;
                margin-left: 5px;
                font-weight: bold;
                text-shadow: 0 0 2px var(--neon-blue);
            }
            
            /* Main content layout */
            .main-layout {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            
            .main-container {
                flex: 1;
                display: flex;
                overflow: hidden;
            }
            
            .sidebar {
                width: 200px;
                background-color: var(--win98-gray);
                border-right: 2px solid var(--win98-dark-gray);
                padding: 10px;
                overflow-y: auto;
                background-image: var(--menu-gradient);
            }
            
            .main-content {
                flex: 1;
                padding: 10px;
                overflow: auto;
                background: linear-gradient(135deg, rgba(192, 192, 192, 0.7), rgba(223, 223, 223, 0.7));
            }
            
            /* Icon grid */
            .desktop-icons {
                display: grid;
                grid-template-columns: repeat(auto-fill, 80px);
                grid-gap: 20px;
                padding: 20px;
            }
            
            .desktop-icon {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                cursor: pointer;
                width: 80px;
            }
            
            .desktop-icon img {
                width: 32px;
                height: 32px;
                margin-bottom: 5px;
            }
            
            .desktop-icon span {
                color: white;
                text-shadow: 1px 1px 1px black;
                font-size: 12px;
                max-width: 80px;
                word-wrap: break-word;
            }
            
            /* Animation for button clicks */
            @keyframes click-animation {
                0% { transform: scale(1); }
                50% { transform: scale(0.95); }
                100% { transform: scale(1); }
            }
            
            /* Glow effect for focused elements */
            .glow-focus:focus {
                box-shadow: 0 0 15px var(--neon-blue);
                outline: none;
            }
            
            /* Add scanlines effect to mimic CRT displays */
            .desktop:after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: repeating-linear-gradient(
                    0deg,
                    rgba(0, 0, 0, 0.03),
                    rgba(0, 0, 0, 0.03) 1px,
                    transparent 1px,
                    transparent 2px
                );
                pointer-events: none;
                z-index: 10;
                opacity: 0.5;
            }
            
            /* Add vignette effect */
            .desktop:before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.4);
                pointer-events: none;
                z-index: 5;
            }
            
            /* Window controls */
            .window-controls {
                display: flex;
                align-items: center;
            }
            
            .control-button {
                width: 16px;
                height: 14px;
                margin-left: 4px;
                background-color: var(--win98-gray);
                border-top: 1px solid white;
                border-left: 1px solid white;
                border-right: 1px solid var(--win98-dark-gray);
                border-bottom: 1px solid var(--win98-dark-gray);
                position: relative;
                cursor: pointer;
            }
            
            .control-button:active {
                border-top: 1px solid var(--win98-dark-gray);
                border-left: 1px solid var(--win98-dark-gray);
                border-right: 1px solid white;
                border-bottom: 1px solid white;
            }
            
            .control-button.close::before,
            .control-button.close::after {
                content: '';
                position: absolute;
                width: 8px;
                height: 2px;
                background-color: black;
                top: 6px;
                left: 4px;
            }
            
            .control-button.close::before {
                transform: rotate(45deg);
            }
            
            .control-button.close::after {
                transform: rotate(-45deg);
            }
            
            .control-button.maximize::before {
                content: '';
                position: absolute;
                width: 8px;
                height: 8px;
                border: 1px solid black;
                top: 2px;
                left: 3px;
            }
            
            .control-button.minimize::before {
                content: '';
                position: absolute;
                width: 8px;
                height: 2px;
                background-color: black;
                top: 6px;
                left: 4px;
            }
            
            /* Cyber text effect */
            .cyber-text {
                position: relative;
                display: inline-block;
                color: white;
                text-shadow: 0 0 2px var(--neon-blue),
                             0 0 10px rgba(0, 178, 255, 0.3);
                letter-spacing: 1px;
                animation: cyber-glow 4s ease-in-out infinite alternate;
            }
            
            @keyframes cyber-glow {
                0% { text-shadow: 0 0 2px var(--neon-blue),
                             0 0 5px rgba(0, 178, 255, 0.3); }
                100% { text-shadow: 0 0 5px var(--neon-blue),
                             0 0 15px rgba(138, 43, 226, 0.5); }
            }
            
            /* Form styling */
            .win98-form input,
            .win98-form textarea,
            .win98-form select {
                transition: box-shadow 0.3s ease;
            }
            
            .win98-form input:focus,
            .win98-form textarea:focus,
            .win98-form select:focus {
                box-shadow: 0 0 8px var(--neon-blue);
            }
            
            /* Status bar items */
            .status-item {
                padding: 0 10px;
                border-right: 1px solid var(--win98-dark-gray);
                display: flex;
                align-items: center;
                height: 100%;
            }
            
            .active-connection {
                color: var(--win98-blue);
                position: relative;
            }
            
            .active-connection:after {
                content: '';
                display: inline-block;
                width: 6px;
                height: 6px;
                background-color: var(--neon-blue);
                border-radius: 50%;
                margin-left: 5px;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 0.3; box-shadow: 0 0 0 0 rgba(0, 178, 255, 0.7); }
                70% { opacity: 1; box-shadow: 0 0 0 5px rgba(0, 178, 255, 0); }
                100% { opacity: 0.3; }
            }
            
            /* Line Awesome Windows 98 styling */
            .la {
                color: var(--win98-dark-gray);
                /* For Windows 98 feel, avoid anti-aliasing */
                -webkit-font-smoothing: none;
                -moz-osx-font-smoothing: grayscale;
            }
            
            /* For disabled icons */
            .la.disabled {
                color: var(--win98-dark-gray);
                opacity: 0.5;
            }
            
            /* Standard sizes */
            .la-sm { font-size: 12px; } /* For small context icons */
            .la-md { font-size: 16px; } /* Standard icon size */
            .la-lg { font-size: 24px; } /* For emphasized elements */
            
            /* Win98 icon style class */
            .win98-icon {
                image-rendering: pixelated;
                font-size: 16px;
                /* Optional: add very slight pixel-like border */
                text-shadow: 
                    0.5px 0 0 var(--win98-dark-gray),
                    0 0.5px 0 var(--win98-dark-gray);
            }
            
            /* Apply Windows 98 color scheme to icons */
            .win98-icon.primary {
                color: var(--win98-dark-blue);
            }
            
            .win98-icon.destructive {
                color: var(--win98-red);
            }
            
            .win98-icon.success {
                color: var(--win98-green);
            }
        """
                
        # Creating a separate script block to avoid JavaScript syntax being interpreted as Python
        clock_script = """
            // Simple clock for the status bar
            function updateClock() {
                var now = new Date();
                var hours = now.getHours();
                var minutes = now.getMinutes().toString().padStart(2, '0');
                var ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12; // the hour '0' should be '12'
                document.getElementById('clock').textContent = hours + ':' + minutes + ' ' + ampm;
            }
            
            setInterval(updateClock, 1000);
            updateClock();
        """
        
        draggable_script = """
            // Make the window draggable
            var windowTitle = document.querySelector('.win98-window-title');
            var window = document.querySelector('.win98-window');
            
            var isDragging = false;
            var offsetX, offsetY;
            
            windowTitle.addEventListener('mousedown', function(e) {
                isDragging = true;
                offsetX = e.clientX - window.getBoundingClientRect().left;
                offsetY = e.clientY - window.getBoundingClientRect().top;
            });
            
            document.addEventListener('mousemove', function(e) {
                if (!isDragging) return;
                
                window.style.left = (e.clientX - offsetX) + 'px';
                window.style.top = (e.clientY - offsetY) + 'px';
                window.style.position = 'absolute';
            });
            
            document.addEventListener('mouseup', function() {
                isDragging = false;
            });
        """
        
        breadcrumb_script = """
            // Track the current path to detect changes
            var lastPath = window.location.pathname;
            
            // Function to update breadcrumbs based on current URL
            function updateBreadcrumb() {
                var path = window.location.pathname;
                
                // Only update if the path changed
                if (path !== lastPath) {
                    lastPath = path;
                    var parts = path.split('/').filter(function(p) { return p; });
                    var breadcrumb = '';
                    
                    if (parts.length > 0) {
                        parts.forEach(function(part, index) {
                            var displayPart = part.replace('_', ' ');
                            displayPart = displayPart.charAt(0).toUpperCase() + displayPart.slice(1);
                            
                            breadcrumb += '<span style="margin: 0 5px;">&gt;</span>';
                            breadcrumb += '<span>' + displayPart + '</span>';
                        });
                        
                        document.getElementById('breadcrumb-path').innerHTML = breadcrumb;
                    } else {
                        document.getElementById('breadcrumb-path').innerHTML = '';
                    }
                }
            }
            
            // Listen for popstate events (browser back/forward)
            window.addEventListener('popstate', function() {
                updateBreadcrumb();
            });
            
            // Listen for htmx:pushedIntoHistory
            document.addEventListener('htmx:pushedIntoHistory', function() {
                updateBreadcrumb();
            });
            
            // Listen for htmx:beforeSwap
            document.addEventListener('htmx:beforeSwap', function(event) {
                // Get the URL that's being loaded
                if (event.detail && event.detail.pathInfo && event.detail.pathInfo.finalPath) {
                    lastPath = event.detail.pathInfo.finalPath;
                }
            });
            
            // Listen for htmx:afterSwap and afterSettle
            document.addEventListener('htmx:afterSwap', updateBreadcrumb);
            document.addEventListener('htmx:afterSettle', updateBreadcrumb);
            
            // Also set up a polling fallback to catch any missed updates
            setInterval(updateBreadcrumb, 100);
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', updateBreadcrumb);
            
            // Run immediately for first page load
            updateBreadcrumb();
        """
        
        # Memory usage simulation script
        memory_usage_script = """
            // Memory usage simulation for status bar
            function updateMemoryUsage() {
                const minUsage = 78;
                const maxUsage = 93;
                const usage = Math.floor(Math.random() * (maxUsage - minUsage + 1)) + minUsage;
                document.getElementById('memory-usage').textContent = `RAM: ${usage}%`;
            }
            setInterval(updateMemoryUsage, 5000);
            updateMemoryUsage();
        """
        
        # The actual HTML structure
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Arca CMS</title>
            
            <!-- Line Awesome Icons -->
            <link rel="stylesheet" href="https://maxst.icons8.com/vue-static/landings/line-awesome/line-awesome/1.3.0/css/line-awesome.min.css">
            
            <style>
                {custom_styles}
            </style>
            
            <!-- HTMX for interactions -->
            <script src="https://unpkg.com/htmx.org@1.9.2"></script>
        </head>
        <body>
            <div class="desktop">
                <!-- Main layout -->
                <div class="main-layout">
                    <div class="main-container">
                        <!-- Sidebar with Windows 98 styling -->
                        <div class="sidebar">
                            <div class="win98-window" style="margin-bottom: 15px; width: 100%;">
                                <div class="win98-window-title">
                                    <div style="display: flex; align-items: center;">
                                        <i class="las la-folder la-md win98-icon primary" style="margin-right: 6px;"></i>
                                        <span class="cyber-text">Explorer</span>
                                    </div>
                                </div>
                                
                                <div style="padding: 10px;">
                                    <div style="margin-left: 5px;">
                                        <div style="display: flex; align-items: center; margin-bottom: 10px; cursor: pointer;" 
                                   hx-get="/" 
                                   hx-target="#content-area" 
                                   hx-push-url="true">
                                            <i class="las la-home la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span style="font-weight: bold;">Home</span>
                                        </div>
                                        
                                        <!-- Content section -->
                                        <div style="margin-bottom: 8px; margin-top: 12px;">
                                            <div style="font-weight: bold; color: #000080; margin-bottom: 6px; font-size: 11px;">CONTENT</div>
                                            <div class="win98-separator" style="margin-bottom: 6px;"></div>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/list/pages"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-file-alt la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>Pages</span>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/list/articles"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-newspaper la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>Articles</span>
                                        </div>
                                        
                                        <!-- Administration section -->
                                        <div style="margin-bottom: 8px; margin-top: 12px;">
                                            <div style="font-weight: bold; color: #000080; margin-bottom: 6px; font-size: 11px;">ADMINISTRATION</div>
                                            <div class="win98-separator" style="margin-bottom: 6px;"></div>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/list/users"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-user la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>Users</span>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/list/system"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-cog la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>System</span>
                                        </div>
                                        
                                        <!-- Help section -->
                                        <div style="margin-bottom: 8px; margin-top: 12px;">
                                            <div style="font-weight: bold; color: #000080; margin-bottom: 6px; font-size: 11px;">HELP</div>
                                            <div class="win98-separator" style="margin-bottom: 6px;"></div>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/help"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-question-circle la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>Documentation</span>
                                        </div>
                                        
                                        <div style="display: flex; align-items: center; margin-bottom: 6px; cursor: pointer;"
                                             hx-get="/about"
                                             hx-target="#content-area"
                                             hx-push-url="true">
                                            <i class="las la-info-circle la-md win98-icon primary" style="margin-right: 5px;"></i>
                                            <span>About</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Content area -->
                        <div class="main-content">
                            <!-- Breadcrumb navigation with improved styling -->
                            <div class="win98-panel" style="margin-bottom: 10px; padding: 5px; display: flex; align-items: center;">
                                <div style="display: flex; align-items: center; margin-right: 15px; cursor: pointer;"
                                     hx-get="/"
                                     hx-target="#content-area"
                                     hx-push-url="true">
                                    <i class="las la-home la-md win98-icon primary" style="margin-right: 5px;"></i>
                                    <span>Home</span>
                                </div>
                                <div id="breadcrumb-path" style="display: flex; align-items: center;">
                                </div>
                                
                                <!-- Quick action buttons -->
                                <div style="margin-left: auto; display: flex; gap: 5px;">
                                    <button class="win98-btn" style="font-size: 11px; padding: 2px 5px; display: flex; align-items: center;"
                                            hx-get="/new/page"
                                            hx-target="#content-area"
                                            hx-push-url="true">
                                        <i class="las la-file la-sm win98-icon" style="margin-right: 3px;"></i>
                                        New Page
                                    </button>
                                    <button class="win98-btn" style="font-size: 11px; padding: 2px 5px; display: flex; align-items: center;"
                                            hx-get="/new/article"
                                            hx-target="#content-area"
                                            hx-push-url="true">
                                        <i class="las la-newspaper la-sm win98-icon" style="margin-right: 3px;"></i>
                                        New Article
                                    </button>
                                </div>
                            </div>
                            
                            <main>
                                <div id="content-area" class="win98-panel-inset" style="padding: 10px; height: calc(100% - 40px); overflow: auto; background-color: white;">
                                    {children or self._render_desktop()}
                                </div>
                            </main>
                        </div>
                    </div>
                    
                    <!-- Status bar with additional indicators -->
                    <div class="status-bar">
                        <div class="status-item">Ready</div>
                        <div class="status-item active-connection">Connected</div>
                        <div class="status-item" style="margin-left: auto;" id="clock"></div>
                        <div class="status-item" onclick="location.reload()" style="cursor: pointer; color: var(--win98-blue);">Refresh</div>
                        <div class="status-item" style="min-width: 80px;" id="memory-usage">RAM: 82%</div>
                    </div>
                </div>
            </div>
            
            <!-- Scripts -->
            <script>
                {clock_script}
            </script>
            <script>
                {draggable_script}
            </script>
            <script>
                {breadcrumb_script}
            </script>
            <script>
                {memory_usage_script}
            </script>
        </body>
        </html>
        """

    def _render_desktop(self):
        """
        Render a Windows 98 desktop-style homepage with icons
        
        Returns:
            str: The rendered HTML for the desktop
        """
        return """
        <div style="height: 100%; display: flex; flex-direction: column;">
            <!-- Desktop icons -->
            <div class="desktop-icons" style="padding: 20px; flex: 1;">
                <!-- Content icons -->
                <div class="desktop-icon" 
                     hx-get="/list/pages" 
                     hx-target="#content-area" 
                     hx-push-url="true">
                    <i class="las la-file-alt win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Pages</div>
                </div>
                
                <div class="desktop-icon" 
                     hx-get="/list/articles" 
                     hx-target="#content-area" 
                     hx-push-url="true">
                    <i class="las la-newspaper win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Articles</div>
                </div>
                
                <div class="desktop-icon"
                     hx-get="/list/media"
                     hx-target="#content-area"
                     hx-push-url="true">
                    <i class="las la-image win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Media</div>
                </div>
                
                <!-- Administration icons -->
                <div class="desktop-icon"
                     hx-get="/list/users" 
                     hx-target="#content-area" 
                     hx-push-url="true">
                    <i class="las la-user win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Users</div>
                </div>
                
                <div class="desktop-icon"
                     hx-get="/list/system" 
                     hx-target="#content-area" 
                     hx-push-url="true">
                    <i class="las la-cog win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">System</div>
                </div>
                
                <div class="desktop-icon"
                     hx-get="/help" 
                     hx-target="#content-area" 
                     hx-push-url="true">
                    <i class="las la-question-circle win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Help</div>
                </div>
                
                <!-- Recycle Bin icon -->
                <div class="desktop-icon" onclick="emptyRecycleBin(event)">
                    <i class="las la-trash win98-icon primary" style="font-size: 32px; margin-bottom: 5px;"></i>
                    <div class="desktop-icon-label">Recycle Bin</div>
                </div>
            </div>
            
            <!-- Welcome message -->
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                <div class="win98-window" style="width: 350px; box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);">
                    <div class="win98-window-title">
                        <div style="display: flex; align-items: center;">
                            <i class="las la-info-circle la-md win98-icon primary" style="margin-right: 5px;"></i>
                            <span>Welcome to Arca CMS</span>
                        </div>
                        <div class="window-controls">
                            <button class="control-button minimize"></button>
                            <button class="control-button maximize"></button>
                            <button class="control-button close"></button>
                        </div>
                    </div>
                    
                    <div style="padding: 15px; text-align: center;">
                        <i class="las la-desktop win98-icon primary" style="font-size: 64px; margin-bottom: 10px;"></i>
                        <h2 style="font-size: 14px; margin-bottom: 10px;">Welcome to Arca CMS</h2>
                        <p style="font-size: 11px; margin-bottom: 15px;">Get started by exploring the content library or creating new items.</p>
                        <div style="display: flex; justify-content: center; gap: 5px;">
                            <button class="win98-btn" style="font-size: 11px; padding: 3px 8px;"
                                    hx-get="/new/page"
                                    hx-target="#content-area"
                                    hx-push-url="true">
                                Create Page
                            </button>
                            <button class="win98-btn" style="font-size: 11px; padding: 3px 8px;"
                                    hx-get="/list/articles"
                                    hx-target="#content-area"
                                    hx-push-url="true">
                                View Articles
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            .desktop-icon {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                padding: 5px;
                margin-bottom: 10px;
                text-align: center;
                position: relative;
            }
            
            .desktop-icon:hover {
                background-color: rgba(0, 0, 128, 0.1);
            }
            
            .desktop-icon:active {
                background-color: rgba(0, 0, 128, 0.3);
            }
            
            .desktop-icon-img {
                width: 32px;
                height: 32px;
                margin-bottom: 5px;
            }
            
            .desktop-icon-label {
                color: #000;
                font-size: 11px;
                width: 70px;
                text-align: center;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        </style>
        
        <script>
            // Desktop icon drag functionality
            document.querySelectorAll('.desktop-icon').forEach(icon => {
                icon.addEventListener('mousedown', function(e) {
                    if (e.button !== 0) return; // Only left mouse button
                    
                    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                    let isDragging = false;
                    
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    
                    document.onmousemove = dragMouseMove;
                    document.onmouseup = closeDragElement;
                    
                    // Add a small delay to distinguish between click and drag
                    setTimeout(() => {
                        isDragging = true;
                    }, 100);
                    
                    function dragMouseMove(e) {
                        if (!isDragging) return;
                        
                        e.preventDefault();
                        pos1 = pos3 - e.clientX;
                        pos2 = pos4 - e.clientY;
                        pos3 = e.clientX;
                        pos4 = e.clientY;
                        
                        icon.style.position = 'absolute';
                        icon.style.top = (icon.offsetTop - pos2) + "px";
                        icon.style.left = (icon.offsetLeft - pos1) + "px";
                    }
                    
                    function closeDragElement() {
                        document.onmouseup = null;
                        document.onmousemove = null;
                        
                        // If it wasn't a drag, treat as a click
                        if (!isDragging) {
                            const hxGet = icon.getAttribute('hx-get');
                            if (hxGet) {
                                // Trigger HTMX get
                                htmx.ajax('GET', hxGet, {target: '#content-area', pushUrl: true});
                            }
                        }
                    }
                });
            });
            
            // Recycle bin empty functionality
            function emptyRecycleBin(event) {
                event.preventDefault();
                event.stopPropagation();
                
                if (confirm('Are you sure you want to empty the Recycle Bin?')) {
                    alert('Recycle Bin emptied');
                }
            }
        </script>
        """ 