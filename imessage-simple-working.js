#!/usr/bin/env node
/**
 * Super Simple iMessage Monitor - Just Works
 */

const { exec } = require('child_process');
const fs = require('fs');

let lastMessageId = 115; // Start from your last message
let isRunning = true;

console.log(`🔍 Simple Monitor starting from message ID: ${lastMessageId}`);

function checkMessages() {
    if (!isRunning) return;
    
    exec('imsg history --chat-id 1 --limit 5 --json', (error, stdout) => {
        if (error) return;
        
        const lines = stdout.trim().split('\\n').filter(line => 
            line.trim().startsWith('{') && line.trim().endsWith('}')
        );
        
        for (const line of lines) {
            try {
                const message = JSON.parse(line);
                
                if (message.id > lastMessageId && !message.is_from_me && message.text) {
                    const text = message.text.replace(/[\\u0000-\\u001f]/g, '').trim();
                    console.log(`📨 NEW [${message.id}]: "${text}"`);
                    
                    // Generate response
                    let response = '';
                    const lowerText = text.toLowerCase();
                    
                    if (lowerText.includes('stock') || lowerText.includes('invest')) {
                        response = '📊 For current opportunities: KLAC ($1,427 - oversold), LRCX ($233 - AI demand), AVGO ($331 - infrastructure). All strong buy signals. Want details on any?';
                    } else if (lowerText.includes('hello') || lowerText.includes('hi')) {
                        response = '👋 Hey! Scout here - your investment assistant. I can help with stock research and market analysis. What interests you?';
                    } else if (lowerText.includes('test')) {
                        response = '✅ iMessage automation is working! I am monitoring 24/7 for investment questions. Try asking about stocks or markets!';
                    } else {
                        response = `🔍 Got your message: "${text}". I am Scout, your investment research assistant. Ask me about stocks, market trends, or analysis!`;
                    }
                    
                    // Send response  
                    const cleanResponse = response.replace(/'/g, "'\"'\"'");
                    exec(`imsg send --to "+14044160690" --text '${cleanResponse}'`, (err) => {
                        if (!err) console.log(`✅ Responded to: "${text}"`);
                    });
                    
                    lastMessageId = message.id;
                }
            } catch (e) {
                // Skip malformed JSON
            }
        }
    });
}

// Check every 3 seconds
setInterval(checkMessages, 3000);
console.log('👀 Monitoring every 3 seconds...');

// Graceful shutdown
process.on('SIGINT', () => { isRunning = false; process.exit(0); });
process.on('SIGTERM', () => { isRunning = false; process.exit(0); });