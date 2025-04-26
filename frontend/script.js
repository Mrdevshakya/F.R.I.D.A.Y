// Function to create background elements with enhanced sci-fi appearance
function createBackgroundElements() {
    const container = document.querySelector('.container');
    
    // Create subtle background elements
    for (let i = 0; i < 25; i++) {
        const element = document.createElement('div');
        element.className = 'bg-element';
        
        // Random properties for diversity
        const width = Math.random() * 150 + 50;
        const height = Math.random() * 1.2 + 0.5;
        const rotate = Math.random() * 360;
        const duration = Math.random() * 5 + 3;
        const floatDistance = Math.random() * 30 + 10;
        
        element.style.cssText = `
            width: ${width}px;
            height: ${height}px;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            --rotate: ${rotate}deg;
            --duration: ${duration}s;
            --float-distance: ${floatDistance}px;
        `;
        
        container.appendChild(element);
    }
    
    // Create interactive circuit elements
    createInteractiveCircuits();
}

// Create interactive circuit paths that follow cursor movement
function createInteractiveCircuits() {
    const container = document.querySelector('.container');
    const circuitCanvas = document.createElement('canvas');
    circuitCanvas.className = 'circuit-canvas';
    circuitCanvas.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
        opacity: 0.15;
    `;
    
    container.appendChild(circuitCanvas);
    
    const ctx = circuitCanvas.getContext('2d');
    let mouseX = 0;
    let mouseY = 0;
    let nodes = [];
    
    // Set canvas size
    function resizeCanvas() {
        circuitCanvas.width = container.offsetWidth;
        circuitCanvas.height = container.offsetHeight;
        createNodes();
    }
    
    // Create circuit nodes
    function createNodes() {
        nodes = [];
        const nodeCount = Math.min(15, Math.floor(circuitCanvas.width * circuitCanvas.height / 40000));
        
        for (let i = 0; i < nodeCount; i++) {
            nodes.push({
                x: Math.random() * circuitCanvas.width,
                y: Math.random() * circuitCanvas.height,
                radius: Math.random() * 3 + 1,
                connections: []
            });
        }
        
        // Add connections between nodes
        for (let i = 0; i < nodes.length; i++) {
            const connectionCount = Math.floor(Math.random() * 2) + 1;
            const potentialConnections = [...nodes];
            potentialConnections.splice(i, 1);
            
            // Sort by distance
            potentialConnections.sort((a, b) => {
                const distA = Math.hypot(nodes[i].x - a.x, nodes[i].y - a.y);
                const distB = Math.hypot(nodes[i].x - b.x, nodes[i].y - b.y);
                return distA - distB;
            });
            
            // Connect to closest nodes
            for (let j = 0; j < Math.min(connectionCount, potentialConnections.length); j++) {
                nodes[i].connections.push(potentialConnections[j]);
            }
        }
    }
    
    // Draw the circuit
    function drawCircuit() {
        ctx.clearRect(0, 0, circuitCanvas.width, circuitCanvas.height);
        
        // Calculate cursor influence
        const cursorNode = {
            x: mouseX,
            y: mouseY,
            radius: 5,
            isActive: true
        };
        
        // Draw connections
        for (const node of nodes) {
            for (const connection of node.connections) {
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(connection.x, connection.y);
                
                // Calculate distance to cursor
                const cursorDist = Math.hypot(
                    (node.x + connection.x) / 2 - cursorNode.x, 
                    (node.y + connection.y) / 2 - cursorNode.y
                );
                
                const glow = Math.max(0, 1 - cursorDist / 200);
                ctx.strokeStyle = `rgba(0, 230, 118, ${0.3 + glow * 0.5})`;
                ctx.lineWidth = 0.5 + glow;
                ctx.stroke();
            }
        }
        
        // Draw nodes
        for (const node of nodes) {
            // Calculate distance to cursor
            const cursorDist = Math.hypot(node.x - cursorNode.x, node.y - cursorNode.y);
            const glow = Math.max(0, 1 - cursorDist / 150);
            
            // Draw glow
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius + 3 * glow, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 230, 118, ${0.1 + glow * 0.3})`;
            ctx.fill();
            
            // Draw node
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 230, 118, ${0.4 + glow * 0.6})`;
            ctx.fill();
        }
        
        requestAnimationFrame(drawCircuit);
    }
    
    // Track mouse position
    document.addEventListener('mousemove', (e) => {
        const rect = container.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
    });
    
    // Handle resize
    window.addEventListener('resize', resizeCanvas);
    
    // Initialize
    resizeCanvas();
    drawCircuit();
}

// Elements
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

// Sample responses (fallback if server is not available)
const fridayResponses = [
    "I'm analyzing that information now.",
    "According to my database, that would be correct.",
    "I've searched my records and found several matching results.",
    "That's an interesting question. Let me explain...",
    "I'm processing your request now.",
    "Based on my calculations, I can confirm that's accurate.",
    "I've analyzed the data and have an answer for you.",
    "Let me check my knowledge base for the most current information.",
    "I'm cross-referencing multiple sources to verify that information.",
    "That's a complex question. Here's what I can tell you..."
];

// Typing animation effect
function typeMessage(element, text, speed = 10) {
    let i = 0;
    element.textContent = '';
    
    return new Promise(resolve => {
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        type();
    });
}

// Create a modal for the enlarged image
function createImageModal() {
    // Check if modal already exists
    if (document.getElementById('imageModal')) {
        return;
    }
    
    // Create modal container
    const modal = document.createElement('div');
    modal.id = 'imageModal';
    modal.className = 'image-modal';
    modal.style.display = 'none';
    
    // Create close button
    const closeBtn = document.createElement('span');
    closeBtn.className = 'close-modal';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };
    
    // Create image element
    const modalImg = document.createElement('img');
    modalImg.id = 'modalImage';
    modalImg.className = 'modal-content';
    
    // Add elements to modal
    modal.appendChild(closeBtn);
    modal.appendChild(modalImg);
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Close modal when clicking outside the image
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// Add message to chat
async function addMessage(text, isFriday = false, chartPath = null) {
    // Create message pair container if it doesn't exist or create new one
    let messagePair;
    const lastMessagePair = chatArea.querySelector('.message-pair:last-child');
    
    if (!lastMessagePair || (isFriday && lastMessagePair.querySelector('.friday-message')) || 
        (!isFriday && lastMessagePair.querySelector('.user-message'))) {
        messagePair = document.createElement('div');
        messagePair.classList.add('message-pair');
        chatArea.appendChild(messagePair);
    } else {
        messagePair = lastMessagePair;
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.classList.add(isFriday ? 'friday-message' : 'user-message');
    messagePair.appendChild(messageElement);
    
    // Animate typing for FRIDAY messages
    if (isFriday) {
        // Type the message first
        await typeMessage(messageElement, text, 5);
        
        // Add chart image if provided - AFTER the text is typed
        if (chartPath) {
            try {
                // Wait a short moment to ensure typing is complete
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Create or ensure the modal exists
                createImageModal();
                
                // Create a dedicated container for the chart (separate from the text)
                const chartMessagePair = document.createElement('div');
                chartMessagePair.classList.add('message-pair');
                chatArea.appendChild(chartMessagePair);
                
                const chartContainer = document.createElement('div');
                chartContainer.classList.add('chart-container');
                
                // Add loading indicator before the image loads
                const loadingIndicator = document.createElement('div');
                loadingIndicator.className = 'chart-loading';
                loadingIndicator.innerHTML = '<div class="spinner"></div><div>Loading chart...</div>';
                chartContainer.appendChild(loadingIndicator);
                
                // Create the image element
                const chartImage = document.createElement('img');
                chartImage.style.display = 'none'; // Hide until loaded
                chartImage.alt = 'Stock Analysis Chart';
                chartImage.classList.add('chart-image');
                
                // Set up a load timeout to handle cases where loading takes too long
                let loadTimeout = setTimeout(() => {
                    if (chartImage.style.display === 'none') {
                        console.warn("Chart image load timeout");
                        loadingIndicator.remove();
                        
                        // Show error message
                        const errorContainer = document.createElement('div');
                        errorContainer.className = 'chart-error';
                        
                        const errorText = document.createElement('div');
                        errorText.textContent = "Loading chart timed out. Please try again.";
                        errorText.style.color = "#ff5555";
                        
                        const retryButton = document.createElement('button');
                        retryButton.className = 'retry-button';
                        retryButton.textContent = "Retry";
                        retryButton.onclick = function() {
                            errorContainer.remove();
                            chartImage.src = `/${chartPath}?t=${new Date().getTime()}`;
                        };
                        
                        errorContainer.appendChild(errorText);
                        errorContainer.appendChild(retryButton);
                        chartContainer.appendChild(errorContainer);
                    }
                }, 30000); // 30 second timeout
                
                // Create the image element
                chartImage.src = `/${chartPath}`;
                
                // Handle successful image load
                chartImage.onload = function() {
                    clearTimeout(loadTimeout);
                    console.log("Chart image loaded successfully");
                    // Remove loading indicator and show image
                    if (loadingIndicator.parentNode) {
                        loadingIndicator.remove();
                    }
                    chartImage.style.display = 'block';
                    
                    // Ensure we scroll to show the chart with better browser compatibility
                    setTimeout(() => {
                        // First try scrollIntoView if available
                        if (chartContainer.scrollIntoView) {
                            try {
                                chartContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            } catch (e) {
                                console.warn("scrollIntoView not fully supported, falling back to scrollTop");
                                chatArea.scrollTop = chatArea.scrollHeight;
                            }
                        } else {
                            // Fallback to standard scrollTop
                            chatArea.scrollTop = chatArea.scrollHeight;
                        }
                    }, 200); // Give a bit more time for render
                };
                
                // Handle image load error
                chartImage.onerror = function() {
                    console.error("Error loading chart image from: " + chartPath);
                    
                    // Make sure the loading indicator is removed if it exists
                    if (loadingIndicator && loadingIndicator.parentNode) {
                        loadingIndicator.remove();
                    }
                    
                    // Add error message with retry button
                    const errorContainer = document.createElement('div');
                    errorContainer.className = 'chart-error';
                    
                    const errorText = document.createElement('div');
                    errorText.textContent = "Chart could not be loaded.";
                    errorText.style.color = "#ff5555";
                    
                    const retryButton = document.createElement('button');
                    retryButton.className = 'retry-button';
                    retryButton.textContent = "Retry";
                    retryButton.onclick = function() {
                        // Remove error message
                        errorContainer.remove();
                        
                        // Create new loading indicator if needed
                        const newLoadingIndicator = document.createElement('div');
                        newLoadingIndicator.className = 'chart-loading';
                        newLoadingIndicator.innerHTML = '<div class="spinner"></div><div>Loading chart...</div>';
                        chartContainer.appendChild(newLoadingIndicator);
                        
                        // Attempt to reload the image with cache busting
                        const timestamp = new Date().getTime();
                        chartImage.src = `/${chartPath}?t=${timestamp}`;
                    };
                    
                    errorContainer.appendChild(errorText);
                    errorContainer.appendChild(retryButton);
                    chartContainer.appendChild(errorContainer);
                };
                
                // Add zoom icon and tooltip
                const zoomHint = document.createElement('div');
                zoomHint.className = 'zoom-hint';
                zoomHint.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/><path fill="currentColor" d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z"/></svg> Click to zoom';
                
                // Make the image clickable to open the modal
                chartImage.onclick = function() {
                    const modal = document.getElementById('imageModal');
                    const modalImg = document.getElementById('modalImage');
                    modal.style.display = 'block';
                    modalImg.src = this.src;
                };
                
                // Assemble the chart container
                chartContainer.appendChild(chartImage);
                chartContainer.appendChild(zoomHint);
                
                // Add the chart container to the message pair
                chartMessagePair.appendChild(chartContainer);
            } catch (error) {
                console.error("Error displaying chart:", error);
                // Create an error message if something went wrong
                const errorMessagePair = document.createElement('div');
                errorMessagePair.classList.add('message-pair');
                
                const errorMessage = document.createElement('div');
                errorMessage.classList.add('friday-message', 'error-message');
                errorMessage.textContent = "I had trouble displaying the chart. Please try again.";
                
                errorMessagePair.appendChild(errorMessage);
                chatArea.appendChild(errorMessagePair);
            }
        }
    } else {
        messageElement.textContent = text;
    }
    
    // Scroll to bottom
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Get FRIDAY response from server
async function getFridayResponse(userMessage) {
    try {
        // Connect to the FRIDAY server
        const response = await fetch('/api/friday', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        });
        
        if (!response.ok) {
            throw new Error('Server response was not ok');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error communicating with FRIDAY server:', error);
        // Fallback to sample responses if server is unavailable
        return {
            response: "I'm sorry, I'm having trouble connecting to my brain. " + 
                   fridayResponses[Math.floor(Math.random() * fridayResponses.length)]
        };
    }
}

// Prevent sending while already processing a message
let isSending = false;

// Handle send message
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (message && !isSending) {
        try {
            // Set sending flag to prevent multiple sends
            isSending = true;
            
            // Add user message
            addMessage(message, false);
            
            // Clear input
            userInput.value = '';
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('friday-message', 'typing-indicator');
            typingIndicator.textContent = "...";
            chatArea.appendChild(typingIndicator);
            
            // Get FRIDAY response
            const fridayResponseData = await getFridayResponse(message);
            
            // Remove typing indicator
            if (chatArea.contains(typingIndicator)) {
                chatArea.removeChild(typingIndicator);
            }
            
            // Add FRIDAY response with chart if available
            await addMessage(fridayResponseData.response, true, fridayResponseData.chart_path);
        } catch (error) {
            console.error("Error processing message:", error);
            
            // Remove typing indicator if it exists
            const typingIndicator = chatArea.querySelector('.typing-indicator');
            if (typingIndicator && typingIndicator.parentNode) {
                typingIndicator.parentNode.removeChild(typingIndicator);
            }
            
            // Add error message
            await addMessage("I'm sorry, I encountered an error while processing your request.", true);
        } finally {
            // Reset sending flag
            isSending = false;
        }
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Ensure document is ready before initializing
function documentReady(fn) {
    // See if DOM is already available
    if (document.readyState === "complete" || document.readyState === "interactive") {
        // Call on next available tick
        setTimeout(fn, 1);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

// Add a typing effect to the initial greeting
function animateGreeting(message) {
    const greetingPair = document.createElement('div');
    greetingPair.classList.add('message-pair');
    chatArea.appendChild(greetingPair);
    
    const greetingMessage = document.createElement('div');
    greetingMessage.classList.add('friday-message');
    greetingPair.appendChild(greetingMessage);
    
    // Start with empty content and animate typing
    let i = 0;
    const typingSpeed = 50;
    
    function typeGreeting() {
        if (i < message.length) {
            greetingMessage.textContent += message.charAt(i);
            i++;
            setTimeout(typeGreeting, typingSpeed);
        }
    }
    
    typeGreeting();
}

// Initialize the app
documentReady(() => {
    // Focus input on page load
    if (userInput) {
        userInput.focus();
    }
    
    // Create image modal on load
    createImageModal();
    
    // Add initial greeting after a short delay
    setTimeout(() => {
        animateGreeting("Hello, I'm FRIDAY. How can I assist you today?");
    }, 800);
    
    // Initialize background elements
    createBackgroundElements();
});