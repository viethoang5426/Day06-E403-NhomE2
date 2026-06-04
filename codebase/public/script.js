// ========================================
// AI Travel Planner — TravelBot
// Client-side Logic — Premium Redesign
// ========================================

(function () {
  'use strict';

  // --- State ---
  let chatHistory = []; // { role: 'user'|'assistant', content: '...' }
  let isLoading = false;

  // --- DOM Elements ---
  const chatMessages = document.getElementById('chatMessages');
  const chatArea = document.getElementById('chatArea');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const newChatBtn = document.getElementById('newChatBtn');
  const particleCanvas = document.getElementById('particleCanvas');

  // --- Initialize ---
  function init() {
    setupEventListeners();
    showWelcomeMessage();
    initParticles();
    messageInput.focus();
    autoResizeTextarea();
  }

  // --- Particle Background ---
  function initParticles() {
    if (!particleCanvas) return;
    const ctx = particleCanvas.getContext('2d');
    let particles = [];
    let animationId;
    const particleCount = 40;

    function resize() {
      particleCanvas.width = window.innerWidth;
      particleCanvas.height = window.innerHeight;
    }

    function createParticle() {
      return {
        x: Math.random() * particleCanvas.width,
        y: Math.random() * particleCanvas.height,
        size: Math.random() * 2 + 0.5,
        speedX: (Math.random() - 0.5) * 0.3,
        speedY: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.4 + 0.1,
        pulseSpeed: Math.random() * 0.02 + 0.005,
        pulsePhase: Math.random() * Math.PI * 2,
      };
    }

    function initParticleArray() {
      particles = [];
      for (let i = 0; i < particleCount; i++) {
        particles.push(createParticle());
      }
    }

    function drawParticles() {
      ctx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);

      particles.forEach((p, i) => {
        // Update position
        p.x += p.speedX;
        p.y += p.speedY;
        p.pulsePhase += p.pulseSpeed;

        // Wrap around edges
        if (p.x < 0) p.x = particleCanvas.width;
        if (p.x > particleCanvas.width) p.x = 0;
        if (p.y < 0) p.y = particleCanvas.height;
        if (p.y > particleCanvas.height) p.y = 0;

        const pulseFactor = 0.5 + 0.5 * Math.sin(p.pulsePhase);
        const currentOpacity = p.opacity * pulseFactor;
        const currentSize = p.size * (0.8 + 0.4 * pulseFactor);

        // Draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, currentSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 212, 255, ${currentOpacity})`;
        ctx.fill();

        // Draw connections
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 150) {
            const lineOpacity = (1 - dist / 150) * 0.08;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 212, 255, ${lineOpacity})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      });

      animationId = requestAnimationFrame(drawParticles);
    }

    resize();
    initParticleArray();
    drawParticles();

    window.addEventListener('resize', () => {
      resize();
    });
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

    // Sidebar toggle (mobile)
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', toggleSidebar);
    }
    if (sidebarOverlay) {
      sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // New chat button
    if (newChatBtn) {
      newChatBtn.addEventListener('click', handleNewChat);
    }

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const message = btn.dataset.message;
        if (message) {
          messageInput.value = message;
          autoResizeTextarea();
          updateSendButtonState();
          handleSendMessage();
          closeSidebar();
        }
      });
    });
  }

  // --- Sidebar ---
  function toggleSidebar() {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('open');
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');
  }

  // --- New Chat ---
  function handleNewChat() {
    chatHistory = [];
    chatMessages.innerHTML = '';
    showWelcomeMessage();
    messageInput.focus();
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

  // --- Welcome Message ---
  function showWelcomeMessage() {
    const welcomeHtml = `
      <div class="welcome-hero">
        <div class="welcome-hero-icon">🌏</div>
        <h2>Xin chào! Tôi là TravelBot</h2>
        <p>Trợ lý AI giúp bạn lên kế hoạch du lịch trọn gói — khách sạn, phương tiện & điểm tham quan!</p>
      </div>
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
      <p style="margin-top: 16px; color: var(--text-tertiary); font-size: var(--font-sm); text-align: center;">
        Hãy cho tôi biết bạn muốn đi đâu nhé! 🗺️
      </p>
    `;

    appendMessage('bot', welcomeHtml, true);
  }

  // --- Send Message ---
  async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading) return;

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

    // Fallback: If no markdown block found, try parsing the whole reply as JSON directly
    if (!hasSpecialBlock) {
      try {
        const data = JSON.parse(reply);
        if (data.type === 'recommendation' || data.type === 'form_request' || data.type === 'attraction_request') {
          hasSpecialBlock = true;
          parsedBlocks.push(data);
        }
      } catch (e) {
        // Not a pure JSON string, ignore
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
              <input type="number" min="0" name="children" id="children" placeholder="VD: 0" value="${escapeHtml(prefill.children || '')}">
            </div>
          </div>
          <div class="form-group">
            <label>Ngân sách dự kiến (vnd)</label>
            <input type="number" min="0" name="budget" id="budgetInput" placeholder="VD: 5000000" value="${escapeHtml(prefill.budget || '')}" required>
          </div>
          <button type="submit" class="btn-submit-form">🚀 Gửi thông tin</button>
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
            <strong>${escapeHtml(a.name)}</strong> - ${a.ticketPrice === 0 ? 'Miễn phí' : escapeHtml(formatCurrency(a.ticketPrice))}
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
          <button type="submit" class="btn-submit-form">Tôi sẽ đi tới các điểm trên trong chuyến đi</button>
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

    // Budget scenarios
    if (data.budgetScenarios && data.budgetScenarios.length > 0) {
      html += renderBudgetScenarios(data.budgetScenarios);
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

  // --- Budget Scenarios ---
  function renderBudgetScenarios(scenarios) {
    if (!scenarios || scenarios.length === 0) return '';

    const cardsHtml = scenarios.map(s => {
      let typeClass = 'standard';
      let icon = '💎';
      if (s.type.includes('Tiết kiệm')) {
        typeClass = 'budget';
        icon = '🌱';
      } else if (s.type.includes('Thông dụng')) {
        typeClass = 'standard';
        icon = '⭐';
      } else if (s.type.includes('Tận hưởng')) {
        typeClass = 'luxury';
        icon = '👑';
      }

      return `
        <div class="scenario-card ${typeClass}">
          <div class="scenario-header">
            <span class="scenario-icon">${icon}</span>
            <span class="scenario-title">${escapeHtml(s.type)}</span>
          </div>
          <div class="scenario-body">
            <div class="scenario-item">
              <span class="s-label">Khách sạn:</span>
              <span class="s-value">${escapeHtml(s.hotelName || '')}</span>
              <span class="s-price">${escapeHtml(String(s.hotelTotal || '0đ'))}</span>
            </div>
            <div class="scenario-item">
              <span class="s-label">Đi lại:</span>
              <span class="s-value">${escapeHtml(s.transportName || '')}</span>
              <span class="s-price">${escapeHtml(String(s.transportTotal || '0đ'))}</span>
            </div>
            <div class="scenario-item">
              <span class="s-label">Tham quan:</span>
              <span class="s-value">Các điểm đã chọn</span>
              <span class="s-price">${escapeHtml(String(s.attractionTotal || '0đ'))}</span>
            </div>
          </div>
          <div class="scenario-footer">
            <div class="scenario-total-label">Tổng chi phí</div>
            <div class="scenario-total-value">${escapeHtml(String(s.estimatedTotal || '0đ'))}</div>
          </div>
          <div class="scenario-links" style="display:flex; gap:8px; padding-top:12px;">
            ${s.hotelBookingUrl ? `<a href="${escapeHtml(s.hotelBookingUrl)}" target="_blank" style="flex:1; text-align:center; padding:6px; font-size:12px; background:rgba(255,255,255,0.1); border-radius:4px; text-decoration:none; color:var(--text-primary);">📍 Đặt phòng</a>` : ''}
            ${s.transportBookingUrl ? `<a href="${escapeHtml(s.transportBookingUrl)}" target="_blank" style="flex:1; text-align:center; padding:6px; font-size:12px; background:rgba(255,255,255,0.1); border-radius:4px; text-decoration:none; color:var(--text-primary);">🚌 Đặt xe</a>` : ''}
          </div>
        </div>
      `;
    }).join('');

    return `
      <div>
        <div class="rec-section-title">
          <span class="section-icon">📊</span>
          3 Kịch bản Tổng chi phí ước tính
        </div>
        <div class="budget-scenarios-container">
          ${cardsHtml}
        </div>
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

    if (sender === 'bot') {
      const botAvatar = `
        <div class="message-avatar bot-avatar">
          <svg class="bot-avatar-svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" fill="url(#botGrad)" stroke="url(#botGrad)"></path>
            <defs>
              <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#7df9ff"></stop>
                <stop offset="100%" stop-color="#0077b6"></stop>
              </linearGradient>
            </defs>
          </svg>
          <span class="bot-avatar-glow"></span>
        </div>
      `;

      messageEl.innerHTML = `
        ${botAvatar}
        <div class="message-content">
          <div class="message-header">
            <span class="message-name">TravelBot</span>
            <span class="message-tag">AI Assistant</span>
          </div>
          <div class="message-text">${isHtml ? content : `<p>${content}</p>`}</div>
          <div class="message-actions">
            <button class="message-action-btn copy-btn" title="Sao chép câu trả lời">
              <svg class="copy-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <svg class="check-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </button>
            <button class="message-action-btn speak-btn" title="Đọc câu trả lời">
              <svg class="speak-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              </svg>
              <svg class="mute-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5252" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
                <line x1="1" y1="1" x2="23" y2="23"></line>
                <path d="M9 9v6a3 3 0 0 0 3 3h1.586l4.707 4.707A1 1 0 0 0 20 22V4a1 1 0 0 0-1.707-.707L13.586 8H12a3 3 0 0 0-3 3z"></path>
              </svg>
            </button>
          </div>
        </div>
      `;

      // Attach button action event listeners
      const copyBtn = messageEl.querySelector('.copy-btn');
      const speakBtn = messageEl.querySelector('.speak-btn');

      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          const textToCopy = messageEl.querySelector('.message-text').innerText;
          navigator.clipboard.writeText(textToCopy).then(() => {
            const copyIcon = copyBtn.querySelector('.copy-icon');
            const checkIcon = copyBtn.querySelector('.check-icon');
            if (copyIcon && checkIcon) {
              copyIcon.style.display = 'none';
              checkIcon.style.display = 'inline-block';
              copyBtn.classList.add('active');

              setTimeout(() => {
                copyIcon.style.display = 'inline-block';
                checkIcon.style.display = 'none';
                copyBtn.classList.remove('active');
              }, 2000);
            }
          }).catch(err => {
            console.error('Lỗi khi copy:', err);
          });
        });
      }

      if (speakBtn) {
        let isSpeaking = false;
        let utterance = null;

        speakBtn.addEventListener('click', () => {
          const speakIcon = speakBtn.querySelector('.speak-icon');
          const muteIcon = speakBtn.querySelector('.mute-icon');

          if (isSpeaking) {
            window.speechSynthesis.cancel();
            isSpeaking = false;
            if (speakIcon && muteIcon) {
              speakIcon.style.display = 'inline-block';
              muteIcon.style.display = 'none';
            }
            speakBtn.classList.remove('active');
          } else {
            window.speechSynthesis.cancel();

            const textToSpeak = messageEl.querySelector('.message-text').innerText;
            utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = 'vi-VN';

            utterance.onend = () => {
              isSpeaking = false;
              if (speakIcon && muteIcon) {
                speakIcon.style.display = 'inline-block';
                muteIcon.style.display = 'none';
              }
              speakBtn.classList.remove('active');
            };

            utterance.onerror = () => {
              isSpeaking = false;
              if (speakIcon && muteIcon) {
                speakIcon.style.display = 'inline-block';
                muteIcon.style.display = 'none';
              }
              speakBtn.classList.remove('active');
            };

            window.speechSynthesis.speak(utterance);
            isSpeaking = true;
            if (speakIcon && muteIcon) {
              speakIcon.style.display = 'none';
              muteIcon.style.display = 'inline-block';
            }
            speakBtn.classList.add('active');
          }
        });
      }

    } else {
      messageEl.innerHTML = `
        <div class="message-avatar user-avatar">👤</div>
        <div class="message-content">
          <div class="message-text">${isHtml ? content : `<p>${content}</p>`}</div>
        </div>
      `;
    }

    chatMessages.appendChild(messageEl);
    scrollToBottom();
    return messageEl;
  }

  // --- Typing Indicator ---
  function showTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'message bot';
    el.id = 'typingIndicator';

    const botAvatar = `
      <div class="message-avatar bot-avatar">
        <svg class="bot-avatar-svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" fill="url(#botGrad)" stroke="url(#botGrad)"></path>
          <defs>
            <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#7df9ff"></stop>
              <stop offset="100%" stop-color="#00d4ff"></stop>
            </linearGradient>
          </defs>
        </svg>
        <span class="bot-avatar-glow"></span>
      </div>
    `;

    el.innerHTML = `
      ${botAvatar}
      <div class="message-content">
        <div class="message-header">
          <span class="message-name">TravelBot</span>
          <span class="message-tag">AI Assistant</span>
        </div>
        <div class="message-text">
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
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
