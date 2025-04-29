// Initialize default settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    enableProtection: true,
    showWarnings: true,
    threatsBlocked: 0,
    sitesScanned: 0
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
  const settings = await chrome.storage.local.get(['enableProtection', 'sitesScanned']);
  
  if (!settings.enableProtection) return;
  
  // Increment sites scanned counter
  chrome.storage.local.set({ sitesScanned: (settings.sitesScanned || 0) + 1 });
  
  // Here you would normally call your ML model API
  // For now, we'll use a simple heuristic check
  const suspicious = isSuspiciousUrl(url);
  
  if (suspicious) {
    // Increment threats blocked counter
    const threatsData = await chrome.storage.local.get(['threatsBlocked']);
    chrome.storage.local.set({ threatsBlocked: (threatsData.threatsBlocked || 0) + 1 });
    
    // Alert the user
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "showWarning", url: url });
      }
    });
  }
}

// Simple heuristic check (to be replaced with ML model)
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