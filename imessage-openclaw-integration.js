#!/usr/bin/env node
/**
 * iMessage <-> OpenClaw Session Integration
 * Routes iMessages to main OpenClaw session and sends responses back
 */

const { exec } = require('child_process');
const fs = require('fs');

let lastId = 131; // Start from latest message
console.log('🔍 OpenClaw iMessage Integration starting from ID:', lastId);

function checkMessages() {
    exec('imsg history --chat-id 1 --limit 3 --json', (error, stdout) => {
        if (error) return;
        
        const lines = stdout.trim().split('\n');
        for (const line of lines) {
            if (!line.trim().startsWith('{')) continue;
            
            try {
                const msg = JSON.parse(line);
                if (msg.id <= lastId || msg.is_from_me || !msg.text) continue;
                
                const userMessage = msg.text.trim();
                console.log(`📨 New message [${msg.id}]: "${userMessage}"`);
                
                // Send to OpenClaw session and get response
                sendToOpenClawSession(userMessage, (response) => {
                    if (response && response.trim()) {
                        sendReply(response.trim());
                    } else {
                        sendReply("🔍 Message received but no response generated. Let me know what you'd like help with!");
                    }
                });
                
                lastId = msg.id;
                
            } catch (e) {
                console.error('Parse error:', e.message);
            }
        }
    });
}

function sendToOpenClawSession(message, callback) {
    console.log('🔄 Sending to OpenClaw session:', message);
    
    // Use sessions_send to route message to main session
    const sessionCommand = `openclaw sessions send --sessionKey "agent:main:main" --message "${message.replace(/"/g, '\\"')}" --timeoutSeconds 30`;
    
    exec(sessionCommand, { timeout: 35000 }, (error, stdout, stderr) => {
        if (error) {
            console.error('❌ OpenClaw session error:', error.message);
            callback('Sorry, I encountered an error processing your message. Please try again.');
            return;
        }
        
        let response = stdout.trim();
        
        // Clean up the response
        if (response) {
            // Remove any system messages or metadata
            response = response.replace(/^Session.*$/gm, '').trim();
            response = response.replace(/^Agent.*$/gm, '').trim();
            response = response.replace(/^\[.*\]$/gm, '').trim();
            
            console.log('✅ OpenClaw response received:', response.substring(0, 100) + '...');
        }
        
        callback(response);
    });
}

function sendReply(text) {
    // Split long messages to avoid iMessage limits
    const maxLength = 1000;
    const messages = [];
    
    if (text.length <= maxLength) {
        messages.push(text);
    } else {
        // Split on sentence boundaries
        const sentences = text.split('. ');
        let currentMessage = '';
        
        for (const sentence of sentences) {
            if ((currentMessage + sentence).length <= maxLength) {
                currentMessage += (currentMessage ? '. ' : '') + sentence;
            } else {
                if (currentMessage) messages.push(currentMessage);
                currentMessage = sentence;
            }
        }
        if (currentMessage) messages.push(currentMessage);
    }
    
    // Send each message with a small delay
    messages.forEach((message, index) => {
        setTimeout(() => {
            const cleanMessage = message.replace(/"/g, '\\"');
            exec(`imsg send --to "+14044160690" --text "${cleanMessage}"`, (err) => {
                if (!err) {
                    console.log(`✅ Sent part ${index + 1}/${messages.length}: ${message.substring(0, 50)}...`);
                } else {
                    console.error('❌ Send error:', err.message);
                }
            });
        }, index * 1000); // 1 second delay between parts
    });
}

// Start monitoring
setInterval(checkMessages, 3000);
console.log('👀 Monitoring active - routing to OpenClaw session...');

// Graceful shutdown
process.on('SIGINT', () => process.exit(0));
process.on('SIGTERM', () => process.exit(0));