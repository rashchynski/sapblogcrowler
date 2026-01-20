const http = require('http');
const https = require('https');
const url = require('url');

// Configuration
const PROXY_PORT = 8080;
const CUSTOM_HEADERS = {
    "cookie": "cmapi_gtm_bl=ta-asp-bzi-sp-awct-cts-csm-img-flc-fls-mpm-mpr-m6d-tc-tdc; notice_preferences=1:; AMCV_227AC2D754DCAB340A4C98C6%40AdobeOrg=179643557%7CMCMID%7C92202783647495176869221084005124995884%7CMCAID%7CNONE%7CvVersion%7C5.5.0; notice_gdpr_prefs=0|1::implied|eu; cmapi_cookie_privacy=permit_1|2_functional; __VCAP_ID__=ce07a6c3-0896-4cf4-6549-2887; JSESSIONID=s%3A7YRABM5fW9xhpCyIlTFn-FSp6bvy-KjY.BrX8ajZB87hjMGe7DfMnDVC3iw8KSoz8gVUfLbUwOsg",
};

// Create proxy server
const proxyServer = http.createServer((req, res) => {
    // Parse the target URL from the request
    const targetUrl = req.url.substring(1); // Remove leading slash

    const parsedUrl = url.parse(targetUrl);
    const isHttps = parsedUrl.protocol === 'https:';
    const httpModule = isHttps ? https : http;
    const port = parsedUrl.port || (isHttps ? 443 : 80);

    console.log(`[${new Date().toISOString()}] Proxying ${req.method} ${targetUrl}`);

    // Prepare headers for the target request
    const proxyHeaders = { ...req.headers };

    // Add custom headers
    Object.assign(proxyHeaders, CUSTOM_HEADERS);

    // Options for the target request
    const options = {
        hostname: "https://btpdev-aws-platform-services.dt.launchpad.cfapps.us10.hana.ondemand.com",
        path: "/dynamic_dest/s4pp/" + parsedUrl.path,
        method: req.method,
        headers: proxyHeaders
    };

    // Create request to target server
    const proxyReq = httpModule.request(options, (proxyRes) => {
        // Log response info
        console.log(`[${new Date().toISOString()}] Response ${proxyRes.statusCode} from ${targetUrl}`);

        // Forward status code and headers
        res.writeHead(proxyRes.statusCode, proxyRes.headers);

        // Pipe response data back to client
        proxyRes.pipe(res);
    });

    // Handle errors
    proxyReq.on('error', (err) => {
        console.error(`[${new Date().toISOString()}] Proxy request error:`, err.message);
        if (!res.headersSent) {
            res.writeHead(502, { 'Content-Type': 'text/plain' });
            res.end(`Proxy Error: ${err.message}`);
        }
    });

    // Handle client connection errors
    req.on('error', (err) => {
        console.error(`[${new Date().toISOString()}] Client request error:`, err.message);
        proxyReq.destroy();
    });

    // Handle client disconnect
    req.on('close', () => {
        proxyReq.destroy();
    });

    // Forward request body (for POST, PUT, etc.)
    req.pipe(proxyReq);
});

// Handle server errors
proxyServer.on('error', (err) => {
    console.error('Proxy server error:', err);
});

// Start the server
proxyServer.listen(PROXY_PORT, () => {
    console.log(`🚀 Proxy server running on http://localhost:${PROXY_PORT}`);
    console.log(`📝 Custom headers that will be added to each request:`);
    Object.entries(CUSTOM_HEADERS).forEach(([key, value]) => {
        console.log(`   ${key}: ${value}`);
    });
    console.log(`\n📖 Usage examples:`);
    console.log(`   curl "http://localhost:${PROXY_PORT}/https://httpbin.org/headers"`);
    console.log(`   curl "http://localhost:${PROXY_PORT}/http://example.com"`);
    console.log(`\n🔍 Check the terminal for request/response logs`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down proxy server...');
    proxyServer.close(() => {
        console.log('✅ Proxy server closed');
        process.exit(0);
    });
});