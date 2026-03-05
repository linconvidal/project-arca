console.log('Service Worker: Loading');

// ---------------------------------------------------------------------------
// Base path — derived from SW location. Works for both:
//   Local dev:    /demo/sw.js  → BASE = /demo/
//   GitHub Pages: /project-arca/sw.js → BASE = /project-arca/
// ---------------------------------------------------------------------------
const SW_PATH = new URL(self.location).pathname;
const BASE = SW_PATH.substring(0, SW_PATH.lastIndexOf('/') + 1);
console.log('Service Worker: BASE =', BASE);

self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    event.waitUntil(self.clients.claim());
});

// Static file extensions — these are served normally, never routed to Flask
const STATIC_EXTENSIONS = [
    '.js', '.css', '.html', '.png', '.jpg', '.jpeg', '.gif', '.svg',
    '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml',
    '.txt', '.py', '.wasm', '.mjs', '.zip', '.whl', '.md'
];

// Strip base path to get the Flask route path
// e.g. /project-arca/list/articles → /list/articles
//      /demo/list/articles → /list/articles
function toFlaskPath(pathname) {
    if (pathname.startsWith(BASE)) {
        var stripped = pathname.substring(BASE.length - 1); // keep leading /
        return stripped || '/';
    }
    return pathname;
}

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip cross-origin
    if (url.origin !== self.location.origin) return;

    // Skip static files
    if (STATIC_EXTENSIONS.some(ext => url.pathname.toLowerCase().endsWith(ext))) return;

    // CORS preflight
    if (event.request.method === 'OPTIONS') {
        event.respondWith(new Response(null, {
            status: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, HX-Request, HX-Target, HX-Trigger',
            }
        }));
        return;
    }

    // Everything else goes to Flask
    event.respondWith(handleRequest(event.request));
});


// ---------------------------------------------------------------------------
// Main request handler — the SW acts as the HTTP server
// ---------------------------------------------------------------------------
async function handleRequest(request) {
    const url = new URL(request.url);
    const flaskPath = toFlaskPath(url.pathname);
    const isNavigation = request.mode === 'navigate';

    // -------------------------------------------------------------------
    // Full page navigations (window.location.href, link clicks, form submits)
    // -------------------------------------------------------------------
    if (isNavigation) {
        console.log('Service Worker: Navigation to', flaskPath, request.method);

        try {
            let body = '';
            if (request.method === 'POST') {
                body = await request.text();
            }

            const flaskResponse = await sendToFlask({
                path: flaskPath,
                method: request.method,
                body: body,
                headers: Object.fromEntries(request.headers.entries())
            });

            if (flaskResponse.status === 404) {
                return serveShellWithAutoLoad(flaskPath);
            }

            return serveShellWithContent(flaskResponse.data, flaskPath);
        } catch (e) {
            console.log('Service Worker: Flask unavailable during navigation, using autoload');
            return serveShellWithAutoLoad(flaskPath);
        }
    }

    // -------------------------------------------------------------------
    // HTMX / fetch requests — page is alive, Flask is available
    // -------------------------------------------------------------------
    try {
        let body = '';
        if (request.method === 'POST') {
            body = await request.text();
        }

        const flaskResponse = await sendToFlask({
            path: flaskPath,
            method: request.method,
            body: body,
            headers: Object.fromEntries(request.headers.entries())
        });

        // Flask 404 → fall back to normal fetch
        if (flaskResponse.status === 404) {
            return fetch(request);
        }

        const headers = new Headers({
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
        });

        // Handle redirects
        if (flaskResponse.status === 301 || flaskResponse.status === 302) {
            headers.set('HX-Redirect', flaskResponse.redirect_url || BASE);
            return new Response('', { status: 200, headers });
        }

        return new Response(flaskResponse.data, {
            status: flaskResponse.status || 200,
            headers
        });

    } catch (error) {
        console.error('Service Worker error:', error);
        var msg = error.message.includes('timed out')
            ? 'Python runtime is still loading. Please wait a moment and try again.'
            : 'Error: ' + error.message;
        return new Response(
            '<div class="win98-window"><div class="win98-window-title">Please Wait</div>'
            + '<div style="padding:10px;">' + msg + '</div></div>',
            { status: 503, headers: { 'Content-Type': 'text/html' } }
        );
    }
}


// ---------------------------------------------------------------------------
// Send a request to Flask (running in the main thread via Pyodide)
// ---------------------------------------------------------------------------
function sendToFlask(data) {
    const messageChannel = new MessageChannel();

    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Flask request timed out')), 5000);

        messageChannel.port1.onmessage = (event) => {
            clearTimeout(timeout);
            if (event.data.error) {
                reject(new Error(event.data.error));
            } else {
                resolve(event.data);
            }
        };

        self.clients.matchAll().then(clients => {
            if (clients.length > 0) {
                clients[0].postMessage({
                    type: 'FLASK_REQUEST',
                    ...data
                }, [messageChannel.port2]);
            } else {
                clearTimeout(timeout);
                reject(new Error('No clients available'));
            }
        });
    });
}


// ---------------------------------------------------------------------------
// Serve the app shell with Flask content already injected (instant display).
// ---------------------------------------------------------------------------
async function serveShellWithContent(content, path) {
    try {
        const shell = await fetch(BASE + 'index.html').then(r => r.text());

        const fullPage = shell
            .replace('<!-- SW_CONTENT_PLACEHOLDER -->', content)
            .replace('</head>',
                '<script>window.BASE_PATH="' + BASE + '";window.__preRenderedPath = "' + path.replace(/"/g, '\\"') + '";</script>\n</head>');

        return new Response(fullPage, {
            status: 200,
            headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
    } catch (e) {
        console.error('Error building shell with content:', e);
        return serveShellWithAutoLoad(path);
    }
}


// ---------------------------------------------------------------------------
// Serve the app shell with __autoLoadPath set so Pyodide loads the right
// content after initialization.
// ---------------------------------------------------------------------------
async function serveShellWithAutoLoad(path) {
    try {
        const shell = await fetch(BASE + 'index.html').then(r => r.text());

        const fullPage = shell.replace('</head>',
            '<script>window.BASE_PATH="' + BASE + '";window.__autoLoadPath = "' + path.replace(/"/g, '\\"') + '";</script>\n</head>');

        return new Response(fullPage, {
            status: 200,
            headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
    } catch (e) {
        console.error('Error serving shell:', e);
        return fetch(BASE + 'index.html');
    }
}
