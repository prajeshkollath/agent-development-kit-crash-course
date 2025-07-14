// OAuth2 Handler for Default ADK Interface
(function() {
    'use strict';
    
    // Check for OAuth2 parameters in URL
    function checkOAuth2Parameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const oauthCode = urlParams.get('oauth_code');
        const oauthState = urlParams.get('oauth_state');
        const email = urlParams.get('email');
        
        if (oauthCode && oauthState && email) {
            console.log('OAuth2 parameters detected:', { email, oauthCode, oauthState });
            
            // Extract email from state parameter
            let userEmail = email;
            if (oauthState.includes('|')) {
                userEmail = oauthState.split('|')[1];
            }
            
            // Process OAuth2 callback
            processOAuth2Callback(userEmail, oauthCode, oauthState);
            
            // Clean up URL parameters
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
        }
    }
    
    // Process OAuth2 callback by sending message to agent
    async function processOAuth2Callback(email, authCode, state) {
        try {
            console.log('Processing OAuth2 callback for:', email);
            
            // Wait for the chat interface to be ready
            await waitForChatInterface();
            
            // Send OAuth2 callback message to agent
            const message = `Handle OAuth2 callback for user ${email}. Authorization code: ${authCode}. State: ${state}. Please exchange this code for access tokens and store them for this user.`;
            
            // Find the chat input and send button
            const chatInput = document.querySelector('input[type="text"], textarea, [contenteditable="true"]');
            const sendButton = document.querySelector('button[type="submit"], button:contains("Send"), button:contains("Submit")');
            
            if (chatInput && sendButton) {
                // Set the message
                if (chatInput.tagName === 'INPUT' || chatInput.tagName === 'TEXTAREA') {
                    chatInput.value = message;
                } else {
                    chatInput.textContent = message;
                }
                
                // Trigger input event
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Wait a moment and click send
                setTimeout(() => {
                    sendButton.click();
                }, 500);
                
                console.log('OAuth2 callback message sent to agent');
            } else {
                console.error('Could not find chat input or send button');
            }
            
        } catch (error) {
            console.error('Error processing OAuth2 callback:', error);
        }
    }
    
    // Wait for chat interface to be ready
    function waitForChatInterface() {
        return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
                const chatInput = document.querySelector('input[type="text"], textarea, [contenteditable="true"]');
                const sendButton = document.querySelector('button[type="submit"], button:contains("Send"), button:contains("Submit")');
                
                if (chatInput && sendButton) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                resolve();
            }, 10000);
        });
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkOAuth2Parameters);
    } else {
        checkOAuth2Parameters();
    }
    
    // Also check when page loads (for SPA navigation)
    window.addEventListener('load', checkOAuth2Parameters);
    
})(); 