// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "showWarning") {
    showPhishingWarning(message.url);
  }
});

// Function to display a warning banner
function showPhishingWarning(url) {
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
  
  // Add warning text
  warningBanner.innerHTML = `
    <strong>⚠️ Phishing Warning!</strong> 
    <p>This website may be attempting to steal your personal information.</p>
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

// Analyze page content for phishing indicators
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
    showPhishingWarning(window.location.href);
  }
}

// Run analysis when page is loaded
window.addEventListener('load', analyzePage); 