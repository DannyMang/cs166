// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "showWarning") {
    showPhishingWarning(message.url, message.confidence, message.features);
  }
});

// Function to display a warning banner
function showPhishingWarning(url, confidence, features) {
  // Create warning element
  const warningBanner = document.createElement('div');
  warningBanner.style.position = 'fixed';
  warningBanner.style.top = '0';
  warningBanner.style.left = '0';
  warningBanner.style.width = '100%';
  warningBanner.style.backgroundColor = '#f8d7da';
  warningBanner.style.color = '#721c24';
  warningBanner.style.padding = '10px';
  warningBanner.style.textAlign = 'center';
  warningBanner.style.zIndex = '9999';
  warningBanner.style.fontFamily = 'Arial, sans-serif';
  warningBanner.style.fontSize = '16px';
  warningBanner.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
  
  // Format confidence as percentage
  const confidencePercent = Math.round(confidence * 100);
  
  // Create features list if available
  let featuresHtml = '';
  if (features) {
    featuresHtml = `
      <div style="margin: 10px 0; font-size: 14px; text-align: left; max-width: 600px; margin: 10px auto;">
        <strong>Suspicious features detected:</strong>
        <ul style="margin: 5px 0;">
          ${features.has_https ? '' : '<li>Not using HTTPS</li>'}
          ${features.is_ip ? '<li>Using IP address instead of domain name</li>' : ''}
          ${features.subdomain_count > 2 ? '<li>Excessive number of subdomains</li>' : ''}
          ${features.num_digits > 5 ? '<li>Unusual number of digits in URL</li>' : ''}
        </ul>
      </div>
    `;
  }
  
  // Add warning text
  warningBanner.innerHTML = `
    <strong>⚠️ Phishing Warning!</strong> 
    <p>This website has been detected as a potential phishing attempt (${confidencePercent}% confidence).</p>
    ${featuresHtml}
    <button id="proceed-anyway" style="margin-right: 10px; padding: 5px 10px;">Proceed Anyway</button>
    <button id="go-back" style="padding: 5px 10px;">Go Back</button>
  `;
  
  // Add to page
  document.body.prepend(warningBanner);
  
  // Add event listeners to buttons
  document.getElementById('proceed-anyway').addEventListener('click', () => {
    warningBanner.remove();
  });
  
  document.getElementById('go-back').addEventListener('click', () => {
    history.back();
  });
}

// Analyze page content for additional phishing indicators
function analyzePage() {
  // Get all text content from the page
  const pageText = document.body.innerText.toLowerCase();
  
  // Check for common phishing phrases
  const phishingPhrases = [
    'verify your account',
    'confirm your password',
    'update your payment information',
    'unusual activity',
    'limited time offer',
    'act now',
    'your account will be suspended'
  ];
  
  let suspiciousScore = 0;
  
  for (const phrase of phishingPhrases) {
    if (pageText.includes(phrase)) {
      suspiciousScore += 1;
    }
  }
  
  // Check for password fields
  const passwordFields = document.querySelectorAll('input[type="password"]');
  if (passwordFields.length > 0) {
    // Check if the site is using HTTPS
    if (window.location.protocol !== 'https:') {
      suspiciousScore += 3; // Major red flag: password field on non-HTTPS site
    }
  }
  
  // If score is high enough, show warning
  if (suspiciousScore >= 2) {
    showPhishingWarning(window.location.href, 0.75, {
      has_https: window.location.protocol === 'https:',
      is_ip: false,
      subdomain_count: window.location.hostname.split('.').length - 1,
      num_digits: (window.location.href.match(/\d/g) || []).length
    });
  }
}

// Run analysis when page is loaded
window.addEventListener('load', analyzePage); 