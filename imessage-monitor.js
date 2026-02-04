#!/usr/bin/env node
/**
 * iMessage Monitor for OpenClaw
 * Monitors iMessage chat for incoming messages and routes them to OpenClaw
 */

const { spawn } = require('child_process');
const { exec } = require('child_process');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

class iMessageMonitor {
    constructor() {
        this.chatId = 1;
        this.phoneNumber = '+14044160690';
        this.lastMessageId = null;
        this.isRunning = false;
        
        // OpenClaw Gateway connection
        this.gatewayUrl = 'ws://127.0.0.1:18789';
        this.gatewayToken = '40d151d8cc5d9369353d962f8fe22b3bfa7adfb267d4f235';
        this.ws = null;
        
        this.setupGracefulShutdown();
        this.loadLastMessageId();
    }
    
    async start() {
        console.log('🔍 Starting iMessage Monitor for OpenClaw...');
        this.isRunning = true;
        
        // Get initial message history to establish baseline
        await this.getInitialHistory();
        
        // Start continuous monitoring
        this.startWatching();
        
        // Connect to OpenClaw Gateway
        this.connectToGateway();
    }
    
    async getInitialHistory() {
        return new Promise((resolve) => {
            exec(`imsg history --chat-id ${this.chatId} --limit 1 --json`, (error, stdout, stderr) => {
                if (error) {
                    console.error('Error getting initial history:', error);
                    resolve();
                    return;
                }
                
                try {
                    const lines = stdout.trim().split('\\n').filter(line => line.trim());
                    if (lines.length > 0) {
                        const lastMessage = JSON.parse(lines[0]);
                        this.lastMessageId = lastMessage.id;
                        console.log(`📱 Baseline established - Last message ID: ${this.lastMessageId}`);
                    }
                } catch (e) {
                    console.error('Error parsing initial history:', e);
                }
                resolve();
            });
        });
    }
    
    startWatching() {
        console.log('👀 Starting iMessage watch...');
        
        // Poll for new messages every 2 seconds
        this.watchInterval = setInterval(() => {
            this.checkForNewMessages();
        }, 2000);
    }
    
    checkForNewMessages() {
        exec(`imsg history --chat-id ${this.chatId} --limit 5 --json`, (error, stdout, stderr) => {
            if (error) {
                console.error('Error checking messages:', error);
                return;
            }
            
            try {
                const lines = stdout.trim().split('\\n').filter(line => line.trim());
                for (const line of lines) {
                    const message = JSON.parse(line);
                    
                    // Skip if this is an old message or from us
                    if (message.id <= this.lastMessageId || message.is_from_me) {
                        continue;
                    }
                    
                    // New incoming message!
                    this.handleIncomingMessage(message);
                    this.lastMessageId = message.id;
                    this.saveLastMessageId();
                }
            } catch (e) {
                console.error('Error parsing message history:', e);
            }
        });
    }
    
    handleIncomingMessage(message) {
        console.log(`📨 New message from ${message.sender}: "${message.text}"`);
        
        // Send to OpenClaw for processing
        this.sendToOpenClaw(message.text, (response) => {
            if (response && response.trim()) {
                this.sendReply(response);
            }
        });
    }
    
    sendToOpenClaw(messageText, callback) {
        // For now, let's use a simple approach and execute openclaw CLI
        const command = `echo "${messageText.replace(/"/g, '\\\\"')}" | timeout 30s openclaw agent --agent main --session main`;
        
        exec(command, { timeout: 35000 }, (error, stdout, stderr) => {
            if (error) {
                console.error('Error from OpenClaw:', error);
                callback('Sorry, I encountered an error processing your message.');
                return;
            }
            
            const response = stdout.trim();
            console.log(`🔍 OpenClaw response: "${response}"`);
            callback(response);
        });
    }
    
    sendReply(responseText) {
        const command = `imsg send --to "${this.phoneNumber}" --text "${responseText.replace(/"/g, '\\\\"')}"`;
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('Error sending reply:', error);
                return;
            }
            console.log(`✅ Reply sent: "${responseText}"`);
        });
    }
    
    connectToGateway() {
        // This is for future enhancement - direct WebSocket connection to OpenClaw
        console.log('🌐 Gateway WebSocket connection - planned for future enhancement');
    }
    
    loadLastMessageId() {
        const statePath = path.join(__dirname, 'imessage-state.json');
        if (fs.existsSync(statePath)) {
            try {
                const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
                this.lastMessageId = state.lastMessageId || 0;
                console.log(`📂 Loaded last message ID: ${this.lastMessageId}`);
            } catch (e) {
                console.error('Error loading state:', e);
                this.lastMessageId = 0;
            }
        }
    }
    
    saveLastMessageId() {
        const statePath = path.join(__dirname, 'imessage-state.json');
        const state = { lastMessageId: this.lastMessageId };
        fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
    }
    
    setupGracefulShutdown() {
        process.on('SIGINT', () => {
            console.log('\\n🛑 Shutting down iMessage Monitor...');
            this.stop();
            process.exit(0);
        });
        
        process.on('SIGTERM', () => {
            console.log('\\n🛑 Received SIGTERM, shutting down...');
            this.stop();
            process.exit(0);
        });
    }
    
    stop() {
        this.isRunning = false;
        if (this.watchInterval) {
            clearInterval(this.watchInterval);
        }
        if (this.ws) {
            this.ws.close();
        }
        console.log('🔍 iMessage Monitor stopped');
    }
}

// Start the monitor if this script is run directly
if (require.main === module) {
    const monitor = new iMessageMonitor();
    monitor.start().catch(console.error);
}

module.exports = iMessageMonitor;