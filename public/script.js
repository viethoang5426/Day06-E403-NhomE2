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

    await sendMessage(message, false);
  }

  async function sendMessage(message, isHidden = false) {
    if (!isHidden) {
      // Show user message
      appendMessage('user', escapeHtml(message));
    }

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
    const jsonRegex = /```json\s*([\s\S]*?)```/g;
    let match;
    let hasSpecialBlock = false;
    let parsedBlocks = [];
    
    // First pass: extract valid special JSON blocks
    while ((match = jsonRegex.exec(reply)) !== null) {
      try {
        const data = JSON.parse(match[1]);
        if (data.type === 'recommendation' || data.type === 'form_request' || data.type === 'attraction_request') {
          hasSpecialBlock = true;
          parsedBlocks.push(data);
        }
      } catch (e) {
        // Invalid JSON, ignore
      }
    }
    
    let finalHtml = '';
    
    if (hasSpecialBlock) {
      // Render ONLY the special blocks, hiding extra text
      for (const data of parsedBlocks) {
        if (data.type === 'recommendation') {
          finalHtml += renderRecommendation(data);
        } else if (data.type === 'form_request') {
          finalHtml += renderTravelForm(data.prefill || {});
        } else if (data.type === 'attraction_request') {
          finalHtml += renderAttractionForm(data);
        }
      }
    } else {
      // Normal rendering
      let lastIndex = 0;
      jsonRegex.lastIndex = 0; // reset
      while ((match = jsonRegex.exec(reply)) !== null) {
        const textBefore = reply.substring(lastIndex, match.index).trim();
        if (textBefore) finalHtml += renderMarkdown(textBefore);
        finalHtml += `<pre><code>${escapeHtml(match[1])}</code></pre>`;
        lastIndex = match.index + match[0].length;
      }
      const textAfter = reply.substring(lastIndex).trim();
      if (textAfter) finalHtml += renderMarkdown(textAfter);
    }

    const msgEl = appendMessage('bot', finalHtml || renderMarkdown(reply), true);

    // Attach form submit listeners if any form was rendered
    if (msgEl) {
      const travelForm = msgEl.querySelector('.travel-form');
      if (travelForm) {
        travelForm.addEventListener('submit', handleFormSubmit);
      }
      const attractionForm = msgEl.querySelector('.attraction-form');
      if (attractionForm) {
        attractionForm.addEventListener('submit', handleAttractionFormSubmit);
      }
    }
  }

  // --- Render Form ---
  function renderTravelForm(prefill) {
    return `
      <div class="form-card">
        <div class="form-title">📋 Cung cấp thông tin chuyến đi</div>
        <p class="form-desc">Vui lòng điền các thông tin sau để tôi có thể đề xuất lịch trình tốt nhất cho bạn.</p>
        <form class="travel-form">
          <div class="form-group">
            <label>Nơi đi</label>
            <input type="text" name="departure" placeholder="VD: Hà Nội, TP.HCM..." value="${escapeHtml(prefill.departure || '')}" required>
          </div>
          <div class="form-group">
            <label>Nơi đến</label>
            <input type="text" name="destination" placeholder="VD: Đà Nẵng, Nha Trang, Ninh Bình..." value="${escapeHtml(prefill.destination || '')}" required>
          </div>
          <div class="form-group-row">
            <div class="form-group">
              <label>Ngày khởi hành</label>
              <input type="date" name="startDate" value="${escapeHtml(prefill.startDate || '')}" required>
            </div>
            <div class="form-group">
              <label>Ngày kết thúc</label>
              <input type="date" name="endDate" value="${escapeHtml(prefill.endDate || '')}" required>
            </div>
          </div>
          <div class="form-group-row">
            <div class="form-group">
              <label>Số người lớn</label>
              <input type="number" min="1" name="adults" id="adults" placeholder="VD: 2" value="${escapeHtml(prefill.adults || '')}" required>
            </div>
            <div class="form-group">
              <label>Số trẻ nhỏ</label>
              <input type="number" min="0" name="children" id="children" placeholder="VD: 0" value="${escapeHtml(prefill.children || '')}" required>
            </div>
          </div>
          <div class="form-group">
            <label>Ngân sách dự kiến</label>
            <input type="text" name="budget" id="budgetInput" placeholder="VD: 5 triệu" value="${escapeHtml(prefill.budget || '')}" required>
          </div>
          <button type="submit" class="btn-submit-form">Gửi thông tin</button>
        </form>
      </div>
    `;
  }

  // --- Handle Form Submit ---
  function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const departure = formData.get('departure');
    const destination = formData.get('destination');
    const startDate = formData.get('startDate');
    const endDate = formData.get('endDate');
    const adults = formData.get('adults');
    const children = formData.get('children');
    const budget = formData.get('budget');
    
    // Disable form to prevent multiple submits
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => input.disabled = true);
    
    const msg = `Thông tin chuyến đi của tôi:
- Nơi đi: ${departure}
- Nơi đến: ${destination}
- Ngày khởi hành: ${startDate}
- Ngày kết thúc: ${endDate}
- Người lớn: ${adults}
- Trẻ nhỏ: ${children || 0}
- Ngân sách: ${budget}`;
    
    sendMessage(msg, true);
  }

  // --- Render Attraction Form ---
  function renderAttractionForm(data) {
    if (!data.attractions || data.attractions.length === 0) return '';
    
    const listHtml = data.attractions.map(a => `
      <label class="attraction-item">
        <input type="checkbox" name="attractions" value="${escapeHtml(a.name)}" ${a.precheck ? 'checked' : ''}>
        <div class="attraction-info-box">
          <div class="attraction-info-title">
            <strong>${escapeHtml(a.name)}</strong> - ${escapeHtml(a.price)}
          </div>
          ${a.precheck && a.reason ? `<div class="attraction-reason">✨ ${escapeHtml(a.reason)}</div>` : ''}
        </div>
      </label>
    `).join('');

    return `
      <div class="form-card attraction-form-card">
        <div class="form-title">📍 Lựa chọn địa điểm thăm quan</div>
        <p class="form-desc">Dựa vào thông tin của bạn, AI đã đề xuất sẵn các địa điểm phù hợp nhất. Bạn có thể chọn hoặc bỏ chọn theo ý thích:</p>
        <form class="attraction-form">
          <div class="attraction-list">
            ${listHtml}
          </div>
          <button type="submit" class="btn-submit-form">Xác nhận & Chốt lịch trình</button>
        </form>
      </div>
    `;
  }

  // --- Handle Attraction Form Submit ---
  function handleAttractionFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    
    // Disable form to prevent multiple submits
    const inputs = form.querySelectorAll('input, button');
    inputs.forEach(input => input.disabled = true);
    
    // Get checked values
    const checked = form.querySelectorAll('input[name="attractions"]:checked');
    const checkedNames = Array.from(checked).map(cb => cb.value);

    const msg = `Tôi chọn các địa điểm sau: ${checkedNames.length > 0 ? checkedNames.join(', ') : 'Không chọn địa điểm nào'}. Hãy chốt lịch trình và tính tổng chi phí.`;
    
    sendMessage(msg, true);
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
    return messageEl;
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
