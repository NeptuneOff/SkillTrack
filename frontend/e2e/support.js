export const browserApiUrl = process.env.PLAYWRIGHT_BROWSER_API_URL || 'http://localhost:8000';
export const apiUrl = process.env.PLAYWRIGHT_API_URL || browserApiUrl;

export async function installContainerApiProxy(page) {
  const proxyUrl = process.env.PLAYWRIGHT_API_PROXY_URL;
  if (!proxyUrl) return;
  const allowedOrigin = new URL(
    process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5173',
  ).origin;
  await page.route(`${browserApiUrl}/**`, async (route) => {
    const request = route.request();
    const corsHeaders = {
      'access-control-allow-origin': allowedOrigin,
      'access-control-allow-methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'access-control-allow-headers':
        request.headers()['access-control-request-headers'] || 'authorization, content-type',
      'access-control-max-age': '600',
      vary: 'Origin',
    };
    if (request.method() === 'OPTIONS') {
      await route.fulfill({status: 204, headers: corsHeaders});
      return;
    }
    const response = await route.fetch({
      url: request.url().replace(browserApiUrl, proxyUrl),
    });
    await route.fulfill({response, headers: {...response.headers(), ...corsHeaders}});
  });
}
