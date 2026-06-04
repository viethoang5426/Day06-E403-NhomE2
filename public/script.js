// ========================================
// AI Travel Planner — TravelBot
// Client-side Logic
// ========================================

(function () {
  'use strict';

  // --- State ---
  let apiKey = '';
  let chatHistory = []; // { role: 'user'|'assistant', content: '...' }
  let isLoading = false;

  // --- DOM Elements ---
  const chatMessages = document.getElementById('chatMessages');
  const chatArea = document.getElementById('chatArea');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const saveApiKeyBtn = document.getElementById('saveApiKey');
  const apiKeyStatus = document.getElementById('apiKeyStatus');
  const toggleKeyVisibility = document.getElementById('toggleKeyVisibility');

  // --- Initialize ---
  function init() {
    setupEventListeners();
    showWelcomeMessage();
    messageInput.focus();
    autoResizeTextarea();
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Send message
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);

    // Update send button state
    messageInput.addEventListener('input', updateSendButtonState);

    // Save API Key
    saveApiKeyBtn.addEventListener('click', handleSaveApiKey);
    apiKeyInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSaveApiKey();
      }
    });

    // Toggle API Key visibility
    toggleKeyVisibility.addEventListener('click', () => {
      const isPassword = apiKeyInput.type === 'password';
      apiKeyInput.type = isPassword ? 'text' : 'password';
      toggleKeyVisibility.querySelector('.eye-icon').textContent = isPassword ? '🙈' : '👁️';
    });
  }

  // --- Auto-resize textarea ---
  function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
  }

  // --- Update send button state ---
  function updateSendButtonState() {
    sendButton.disabled = !messageInput.value.trim() || isLoading;
  }

  // --- API Key ---
  function handleSaveApiKey() {
    const key = apiKeyInput.value.trim();
    if (!key) {
      showApiKeyStatus('Vui lòng nhập API Key', 'error');
      return;
    }

    apiKey = key;
    showApiKeyStatus('✓ Đã lưu API Key', 'success');

    // Animate the status
    setTimeout(() => {
      apiKeyStatus.textContent = '';
      apiKeyStatus.className = 'api-key-status';
    }, 3000);
  }

  function showApiKeyStatus(text, type) {
    apiKeyStatus.textContent = text;
    apiKeyStatus.className = `api-key-status ${type}`;
  }

  // --- Welcome Message ---
  function showWelcomeMessage() {
    const welcomeHtml = `
      <p>Xin chào! Tôi là <strong>TravelBot</strong> 🌴</p>
      <p>Tôi sẽ giúp bạn lên kế hoạch du lịch trọn gói — từ khách sạn, phương tiện đến các điểm tham quan hấp dẫn!</p>
      <div class="welcome-features">
        <div class="welcome-feature">
          <span class="welcome-feature-icon">🏨</span>
          <span>Gợi ý khách sạn</span>
        </div>
        <div class="welcome-feature">
          <span class="welcome-feature-icon">✈️</span>
          <span>So sánh phương tiện</span>
        </div>
        <div class="welcome-feature">
          <span class="welcome-feature-icon">🏖️</span>
          <span>Điểm du lịch hấp dẫn</span>
        </div>
        <div class="welcome-feature">
          <span class="welcome-feature-icon">💰</span>
          <span>Tính toán chi phí</span>
        </div>
      </div>
      <p style="margin-top: 12px; color: var(--text-secondary); font-size: var(--font-sm);">
        Hãy cho tôi biết bạn muốn đi du lịch ở đâu nhé! 🗺️
      </p>
    `;

    appendMessage('bot', welcomeHtml, true);
  }

  // --- Send Message ---
  async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    if (!apiKey) {
      showApiKeyStatus('⚠️ Vui lòng nhập API Key trước', 'error');
      apiKeyInput.focus();
      return;
    }

    // Clear input
    messageInput.value = '';
    autoResizeTextarea();
    updateSendButtonState();

    // Show user message
    appendMessage('user', escapeHtml(message));

    // Add to history
    chatHistory.push({ role: 'user', content: message });

    // Show typing indicator
    isLoading = true;
    updateSendButtonState();
    const typingEl = showTypingIndicator();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          message,
          history: chatHistory.slice(0, -1), // exclude current message (already sent separately)
        }),
      });

      // Remove typing indicator
      removeTypingIndicator(typingEl);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || 'Đã xảy ra lỗi, vui lòng thử lại.';

        if (response.status === 401) {
          showApiKeyStatus('⚠️ API Key không hợp lệ', 'error');
        }

        appendMessage('bot', `<div class="error-message">⚠️ ${escapeHtml(errorMsg)}</div>`, true);
        // Remove failed message from history
        chatHistory.pop();
        return;
      }

      const data = await response.json();
      const reply = data.reply;

      // Add assistant reply to history
      chatHistory.push({ role: 'assistant', content: reply });

      // Parse and render reply
      renderBotReply(reply);

    } catch (error) {
      removeTypingIndicator(typingEl);
      console.error('Send message error:', error);
      appendMessage(
        'bot',
        '<div class="error-message">⚠️ Không thể kết nối, vui lòng thử lại sau.</div>',
        true
      );
      chatHistory.pop();
    } finally {
      isLoading = false;
      updateSendButtonState();
      messageInput.focus();
    }
  }

  // --- Render Bot Reply ---
  function renderBotReply(reply) {
    // Check for JSON recommendation block
    const jsonRegex = /```json\s*([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;
    let htmlParts = [];
    let hasRecommendation = false;

    while ((match = jsonRegex.exec(reply)) !== null) {
      // Text before JSON block
      const textBefore = reply.substring(lastIndex, match.index).trim();
      if (textBefore) {
        htmlParts.push(renderMarkdown(textBefore));
      }

      // Try parse JSON
      try {
        const data = JSON.parse(match[1]);
        if (data.type === 'recommendation') {
          htmlParts.push(renderRecommendation(data));
          hasRecommendation = true;
        } else {
          htmlParts.push(`<pre><code>${escapeHtml(match[1])}</code></pre>`);
        }
      } catch (e) {
        htmlParts.push(`<pre><code>${escapeHtml(match[1])}</code></pre>`);
      }

      lastIndex = match.index + match[0].length;
    }

    // Remaining text after last JSON block
    const textAfter = reply.substring(lastIndex).trim();
    if (textAfter) {
      htmlParts.push(renderMarkdown(textAfter));
    }

    const finalHtml = htmlParts.join('');
    appendMessage('bot', finalHtml || renderMarkdown(reply), true);
  }

  // --- Render Recommendation Cards ---
  function renderRecommendation(data) {
    let html = '<div class="recommendation-container">';

    // Summary banner
    if (data.summary) {
      html += `<div class="summary-banner">📋 ${escapeHtml(data.summary)}</div>`;
    }

    // Hotels
    if (data.hotels && data.hotels.length > 0) {
      html += `
        <div>
          <div class="rec-section-title">
            <span class="section-icon">🏨</span>
            Khách sạn đề xuất
          </div>
          <div class="card-grid">
            ${data.hotels.map(renderHotelCard).join('')}
          </div>
        </div>
      `;
    }

    // Transport
    if (data.transport && data.transport.length > 0) {
      html += `
        <div>
          <div class="rec-section-title">
            <span class="section-icon">🚀</span>
            Phương tiện di chuyển
          </div>
          <div class="card-grid">
            ${data.transport.map(renderTransportCard).join('')}
          </div>
        </div>
      `;
    }

    // Attractions
    if (data.attractions && data.attractions.length > 0) {
      html += `
        <div>
          <div class="rec-section-title">
            <span class="section-icon">🏖️</span>
            Điểm du lịch gợi ý
          </div>
          <div class="card-grid">
            ${data.attractions.map(renderAttractionCard).join('')}
          </div>
        </div>
      `;
    }

    // Budget breakdown
    if (data.budgetBreakdown) {
      html += renderBudgetCard(data.budgetBreakdown);
    }

    // Warnings
    if (data.warnings && data.warnings.length > 0) {
      html += `
        <div class="warning-list">
          ${data.warnings.map(w => `
            <div class="warning-item">
              <span class="warning-icon">⚠️</span>
              <span>${escapeHtml(w)}</span>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Price disclaimer
    html += `
      <div class="price-disclaimer">
        <span>ℹ️</span>
        <span>Giá tham khảo — vui lòng kiểm tra lại tại link trước khi thanh toán.</span>
      </div>
    `;

    html += '</div>';
    return html;
  }

  // --- Hotel Card ---
  function renderHotelCard(hotel) {
    const price = formatCurrency(hotel.pricePerNight || hotel.price);
    const tags = (hotel.tags || []).map(t => {
      const isWarning = t.includes('Không phù hợp');
      return `<span class="tag ${isWarning ? 'warning' : ''}">${escapeHtml(t)}</span>`;
    }).join('');

    return `
      <div class="hotel-card">
        ${hotel.image ? `<img src="${escapeHtml(hotel.image)}" alt="${escapeHtml(hotel.name)}" class="hotel-card-image" loading="lazy" onerror="this.style.display='none'">` : ''}
        <div class="hotel-card-body">
          <div class="hotel-card-name">🏨 ${escapeHtml(hotel.name)}</div>
          <div class="hotel-card-meta">
            <span class="hotel-card-rating">⭐ ${hotel.rating || 'N/A'}</span>
            <span class="hotel-card-price">${price}/đêm</span>
            <span class="hotel-card-location">📍 ${escapeHtml(hotel.city || '')}</span>
          </div>
          <div class="hotel-card-desc">${escapeHtml(hotel.description || '')}</div>
          ${tags ? `<div class="hotel-card-tags">${tags}</div>` : ''}
          ${hotel.bookingUrl ? `<a href="${escapeHtml(hotel.bookingUrl)}" target="_blank" rel="noopener noreferrer" class="btn-booking">🔗 Đặt phòng</a>` : ''}
        </div>
      </div>
    `;
  }

  // --- Transport Card ---
  function renderTransportCard(t) {
    const price = formatCurrency(t.price);
    const typeIcon = getTransportIcon(t.type);

    return `
      <div class="transport-card">
        <div class="transport-card-header">
          <span class="transport-type-icon">${typeIcon}</span>
          <span class="transport-provider">${escapeHtml(t.provider || '')}</span>
        </div>
        <div class="transport-route">
          <span>${escapeHtml(t.from || '')}</span>
          <span class="route-arrow">→</span>
          <span>${escapeHtml(t.to || '')}</span>
        </div>
        <div class="transport-details">
          <span>⏱️ ${escapeHtml(t.duration || '')}</span>
          <span class="detail-price">💰 ${price}</span>
        </div>
        ${t.note ? `<div class="transport-note">${escapeHtml(t.note)}</div>` : ''}
        ${t.bookingUrl ? `<a href="${escapeHtml(t.bookingUrl)}" target="_blank" rel="noopener noreferrer" class="btn-booking">🔗 Đặt vé</a>` : ''}
      </div>
    `;
  }

  // --- Attraction Card ---
  function renderAttractionCard(a) {
    const price = a.ticketPrice === 0 ? 'Miễn phí' : formatCurrency(a.ticketPrice);
    const tags = (a.tags || []).map(t => {
      const isWarning = t.includes('Không phù hợp');
      return `<span class="tag ${isWarning ? 'warning' : ''}">${escapeHtml(t)}</span>`;
    }).join('');

    return `
      <div class="attraction-card">
        ${a.image ? `<img src="${escapeHtml(a.image)}" alt="${escapeHtml(a.name)}" class="attraction-card-image" loading="lazy" onerror="this.style.display='none'">` : ''}
        <div class="attraction-card-body">
          <div class="attraction-card-name">🏖️ ${escapeHtml(a.name)}</div>
          <div class="attraction-card-meta">
            <span class="attraction-card-price">🎫 ${price}</span>
            <span class="attraction-card-duration">⏱️ ${escapeHtml(a.suggestedDuration || '')}</span>
          </div>
          <div class="attraction-card-desc">${escapeHtml(a.description || '')}</div>
          ${tags ? `<div class="attraction-card-tags">${tags}</div>` : ''}
        </div>
      </div>
    `;
  }

  // --- Budget Card ---
  function renderBudgetCard(budget) {
    const items = [
      { label: 'Khách sạn', value: budget.hotelTotal },
      { label: 'Phương tiện', value: budget.transportTotal },
      { label: 'Tham quan', value: budget.attractionTotal },
    ];

    const remaining = budget.remainingBudget;
    const isOver = typeof remaining === 'string' && remaining.includes('-');
    const remainingClass = isOver ? 'over' : 'under';

    return `
      <div class="budget-card">
        <div class="budget-card-title">💰 Ước tính chi phí</div>
        ${items.map(item => `
          <div class="budget-item">
            <span>${escapeHtml(item.label)}</span>
            <span class="budget-value">${escapeHtml(String(item.value || '0đ'))}</span>
          </div>
        `).join('')}
        <hr class="budget-divider">
        <div class="budget-item">
          <span><strong>Tổng ước tính</strong></span>
          <span class="budget-value budget-total">${escapeHtml(String(budget.estimatedTotal || ''))}</span>
        </div>
        ${remaining !== undefined ? `
          <div class="budget-item">
            <span>Budget còn lại</span>
            <span class="budget-value budget-remaining ${remainingClass}">${escapeHtml(String(remaining))}</span>
          </div>
        ` : ''}
      </div>
    `;
  }

  // --- Utilities ---
  function getTransportIcon(type) {
    if (!type) return '🚗';
    const t = type.toLowerCase();
    if (t.includes('máy bay') || t.includes('bay')) return '✈️';
    if (t.includes('tàu') || t.includes('tàu hỏa')) return '🚂';
    if (t.includes('xe khách') || t.includes('xe buýt') || t.includes('bus')) return '🚌';
    if (t.includes('xe')) return '🚗';
    return '🚀';
  }

  function formatCurrency(amount) {
    if (typeof amount !== 'number') return String(amount || '0đ');
    return amount.toLocaleString('vi-VN') + 'đ';
  }

  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
  }

  // --- Simple Markdown Renderer ---
  function renderMarkdown(text) {
    if (!text) return '';
    let html = escapeHtml(text);

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic *text*
    html = html.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

    // Newlines
    html = html.replace(/\n/g, '<br>');

    // Bullet lists
    html = html.replace(/(^|<br>)- (.*?)(?=<br>|$)/g, '$1• $2');

    // Numbered lists
    html = html.replace(/(^|<br>)(\d+)\. (.*?)(?=<br>|$)/g, '$1$2. $3');

    return `<div>${html}</div>`;
  }

  // --- Append Message to Chat ---
  function appendMessage(sender, content, isHtml = false) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}`;

    const avatarEmoji = sender === 'bot' ? '🌴' : '👤';

    messageEl.innerHTML = `
      <div class="message-avatar">${avatarEmoji}</div>
      <div class="message-content">${isHtml ? content : `<p>${content}</p>`}</div>
    `;

    chatMessages.appendChild(messageEl);
    scrollToBottom();
  }

  // --- Typing Indicator ---
  function showTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'message bot';
    el.id = 'typingIndicator';
    el.innerHTML = `
      <div class="message-avatar">🌴</div>
      <div class="message-content">
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    chatMessages.appendChild(el);
    scrollToBottom();
    return el;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) {
      el.parentNode.removeChild(el);
    }
  }

  // --- Scroll ---
  function scrollToBottom() {
    requestAnimationFrame(() => {
      chatArea.scrollTop = chatArea.scrollHeight;
    });
  }

  // --- Start ---
  document.addEventListener('DOMContentLoaded', init);
})();
