/**
 * Custom JavaScript for Chainlit Azure Agent
 * Implements persistent user ID via localStorage
 */

// =========================================
// PERSISTENT USER ID (localStorage-based)
// =========================================
function getOrCreatePersistentUserId() {
    const STORAGE_KEY = 'chainlit_user_id';
    
    // Try to get existing user ID from localStorage
    let userId = localStorage.getItem(STORAGE_KEY);
    
    if (!userId) {
        // Generate new UUID v4
        userId = 'user_' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
        
        // Store for future sessions
        localStorage.setItem(STORAGE_KEY, userId);
        console.log('🆕 Generated new persistent user ID:', userId);
    } else {
        console.log('✅ Loaded existing user ID:', userId);
    }
    
    return userId;
}

// Initialize user ID immediately
const PERSISTENT_USER_ID = getOrCreatePersistentUserId();

// Make user ID available globally
window.chainlitUserId = PERSISTENT_USER_ID;

// Send user ID to backend on session start
function sendUserIdToBackend() {
    // Add user ID to session storage for backend access
    sessionStorage.setItem('user_id', PERSISTENT_USER_ID);
    
    // Try to send via Chainlit's session context
    if (window.chainlit && window.chainlit.session) {
        window.chainlit.session.user_id = PERSISTENT_USER_ID;
    }
    
    console.log('📤 User ID available for backend:', PERSISTENT_USER_ID);
}

// Send on load
sendUserIdToBackend();

console.log('🎨 Custom JS loaded - User ID:', PERSISTENT_USER_ID);
