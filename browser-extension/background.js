// Configuration
const API_URL = 'http://localhost:5000';
let protectionEnabled = true;

// Initialize default settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    enableProtection: true,
    showWarnings: true,
    threatsBlocked: 0,
    sitesScanned: 0,
    apiUrl: API_URL
  });
});

// Listen for navigation events
chrome.webNavigation.onCommitted.addListener((details) => {
    if (details.frameId === 0 && protectionEnabled) { // Only check main frame
        checkUrl(details);
    }
});

// Function to check if a URL is potentially malicious
async function checkUrl(details) {
    try {
        // Call the ML model API
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: details.url
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (!result.success) {
            throw new Error('API returned unsuccessful response');
        }

        // Always use the ML model's prediction
        const confidence = result.confidence;
        console.log('ML Model prediction:', confidence);

        if (confidence > 0.4) { // Show warning if confidence > 40%
            // Send warning to content script
            chrome.tabs.sendMessage(details.tabId, {
                action: "showWarning",
                url: details.url,
                confidence: confidence,
                features: result.features
            });
            
            // Update extension badge
            updateBadge(details.tabId, confidence);
            
            // Store threat statistics
            updateStats(true);
        } else {
            // Update stats for non-phishing sites
            updateStats(false);
            console.log('Site deemed safe, confidence:', confidence);
        }
    } catch (error) {
        console.error('Error analyzing page:', error);
        // Only use fallback if API is completely unreachable
        if (!navigator.onLine || error.message.includes('Failed to fetch')) {
            if (isSuspiciousUrl(details.url)) {
                chrome.tabs.sendMessage(details.tabId, {
                    action: "showWarning",
                    url: details.url,
                    confidence: 0.6, // Lower confidence for pattern matching
                    features: {
                        has_https: details.url.startsWith('https://'),
                        is_ip: /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(new URL(details.url).hostname),
                        subdomain_count: details.url.split('.').length - 1,
                        num_digits: (details.url.match(/\d/g) || []).length
                    }
                });
                updateStats(true);
            }
        }
    }
}

// Update the extension badge
function updateBadge(tabId, confidence) {
    const score = Math.round(confidence * 100);
    chrome.action.setBadgeText({
        text: score.toString(),
        tabId: tabId
    });
    
    // Set badge color based on confidence
    const color = score > 75 ? '#ff0000' : // Red for high confidence
                 score > 50 ? '#ff8c00' : // Orange for medium confidence
                 '#008000'; // Green for low confidence
    
    chrome.action.setBadgeBackgroundColor({
        color: color,
        tabId: tabId
    });
}

// Store threat statistics
function updateStats(isPhishing) {
    chrome.storage.local.get(['threatsBlocked', 'sitesScanned'], (result) => {
        const stats = {
            threatsBlocked: (result.threatsBlocked || 0) + (isPhishing ? 1 : 0),
            sitesScanned: (result.sitesScanned || 0) + 1
        };
        chrome.storage.local.set(stats);
    });
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getStats") {
        chrome.storage.local.get(['threatsBlocked', 'sitesScanned'], (result) => {
            sendResponse({
                threatsBlocked: result.threatsBlocked || 0,
                sitesScanned: result.sitesScanned || 0
            });
        });
        return true; // Keep the message channel open for async response
    } else if (message.action === "toggleProtection") {
        protectionEnabled = message.enabled;
        sendResponse({ success: true });
    }
});

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