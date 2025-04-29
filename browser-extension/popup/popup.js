document.addEventListener('DOMContentLoaded', function() {
  // Load stats from storage
  chrome.storage.local.get(['threatsBlocked', 'sitesScanned'], function(result) {
    document.getElementById('threats-blocked').textContent = result.threatsBlocked || 0;
    document.getElementById('sites-scanned').textContent = result.sitesScanned || 0;
  });

  // Load settings
  chrome.storage.local.get(['enableProtection', 'showWarnings'], function(result) {
    document.getElementById('enable-protection').checked = 
      result.enableProtection !== undefined ? result.enableProtection : true;
    document.getElementById('show-warnings').checked = 
      result.showWarnings !== undefined ? result.showWarnings : true;
  });

  // Save settings when changed
  document.getElementById('enable-protection').addEventListener('change', function(e) {
    chrome.storage.local.set({ enableProtection: e.target.checked });
  });

  document.getElementById('show-warnings').addEventListener('change', function(e) {
    chrome.storage.local.set({ showWarnings: e.target.checked });
  });
}); 