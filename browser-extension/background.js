// Initialize default settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    enableProtection: true,
    showWarnings: true,
    threatsBlocked: 0,
    sitesScanned: 0,
    apiUrl: 'http://localhost:5000'  // API server URL
  });
});

// Listen for navigation events to check URLs
chrome.webNavigation.onCommitted.addListener((details) => {
  if (details.frameId === 0) { // Only check main frame
    checkUrl(details.url);
  }
});

// Function to check if a URL is potentially malicious
async function checkUrl(url) {
  // Get settings
  const settings = await chrome.storage.local.get(['enableProtection', 'sitesScanned', 'apiUrl']);
  
  if (!settings.enableProtection) return;
  
  // Increment sites scanned counter
  chrome.storage.local.set({ sitesScanned: (settings.sitesScanned || 0) + 1 });
  
  try {
    // Call the ML model API
    const response = await fetch(`${settings.apiUrl}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });

    if (!response.ok) {
      console.error('API error:', response.statusText);
      return;
    }

    const result = await response.json();
    
    if (result.success && result.is_phishing) {
      // Increment threats blocked counter
      const threatsData = await chrome.storage.local.get(['threatsBlocked']);
      chrome.storage.local.set({ threatsBlocked: (threatsData.threatsBlocked || 0) + 1 });
      
      // Alert the user
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { 
            action: "showWarning", 
            url: url,
            confidence: result.confidence,
            features: result.features
          });
        }
      });
    }
  } catch (error) {
    console.error('Error calling API:', error);
    // Fallback to simple heuristic check if API fails
    if (isSuspiciousUrl(url)) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { 
            action: "showWarning", 
            url: url,
            confidence: 1.0,
            features: null
          });
        }
      });
    }
  }
}

// Simple heuristic check (fallback if API is unavailable)
function isSuspiciousUrl(url) {
  const suspiciousPatterns = [
    'secure-login',
    'account-verify',
    'signin-confirm',
    'banking-secure',
    'paypal-secure',
    'amazon-account',
    'microsoft-verify'
  ];
  
  const urlLower = url.toLowerCase();
  
  // Check for suspicious patterns
  for (const pattern of suspiciousPatterns) {
    if (urlLower.includes(pattern)) {
      return true;
    }
  }
  
  // Check for IP address URLs
  const ipRegex = /https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;
  if (ipRegex.test(url)) {
    return true;
  }
  
  // Check for excessive subdomains
  const domainParts = new URL(url).hostname.split('.');
  if (domainParts.length > 4) {
    return true;
  }
  
  return false;
} 