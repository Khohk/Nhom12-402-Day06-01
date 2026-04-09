import React, { useState, useRef, useEffect } from 'react';
import { FLOW_STATES, INITIAL_MESSAGES } from './mockAgent';
import { callAiAgent } from './api';
import { Send, User, ChevronLeft, Phone, Calendar, Clock, MapPin, CheckCircle } from 'lucide-react';

const App = () => {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [inputText, setInputText] = useState('');
  const [currentState, setCurrentState] = useState(FLOW_STATES.START);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (overrideText = null) => {
    const textToSubmit = overrideText || inputText;
    if (!textToSubmit.trim()) return;

    const userMessage = { role: 'user', content: textToSubmit, type: 'text' };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      // Gọi API AI thật
      const result = await callAiAgent(textToSubmit, messages);
      
      const isWarning = result.reply.includes('🚨') || result.reply.includes('⚠️');
      const isSuccess = result.reply.includes('✅') || result.reply.includes('thành công');
      
      // Tự động phân tách các lựa chọn nếu có danh sách đánh số (ví dụ: 1. **Vinmec**)
      const options = [];
      const optionMatches = result.reply.matchAll(/\d+\.\s+\*\*([^*]+)\*\*/g);
      for (const match of optionMatches) {
        options.push(match[1].trim());
      }
      // Nếu không có markdown đậm, thử tìm list thường
      if (options.length === 0) {
        const plainMatches = result.reply.matchAll(/\d+\.\s+([^\n:]+)/g);
        for (const match of plainMatches) {
            options.push(match[1].trim());
        }
      }

      const botMessage = { 
        role: 'bot', 
        content: result.reply, 
        type: isWarning ? 'warning' : (isSuccess ? 'success' : 'text'),
        data: result.data || null,
        options: options.length > 0 ? options : (result.options || null)
      };
      
      setMessages(prev => [...prev, botMessage]);
      if (result.newState) setCurrentState(result.newState);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: "⚠️ Lỗi hệ thăm: Không thể kết nối tới Agent.", type: 'warning' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const renderMessageContent = (msg, isLast) => {
    // Tách văn bản chính và các lựa chọn
    const lines = msg.content.split('\n');
    const filteredText = [];
    
    lines.forEach(line => {
      // Nếu dòng KHÔNG phải là danh sách đánh số thì mới cho vào text chính
      if (!line.match(/^\d+\.\s+/)) {
        filteredText.push(line);
      }
    });

    const displayContent = filteredText.join('\n').replace(/\n/g, '<br/>');

    return (
      <div className={`message ${msg.role} ${msg.type || ''}`}>
        <div dangerouslySetInnerHTML={{ __html: displayContent }} />
        
        {msg.data?.doctors && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
            {msg.data.doctors.map(doc => (
              <div key={doc.doctor_id || doc.id} className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', cursor: 'pointer' }} onClick={() => handleSend(doc.name)}>
                 <div style={{ width: 44, height: 44, borderRadius: '50%', background: '#f0f4f8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>
                    👨‍⚕️
                 </div>
                 <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: 14 }}>{doc.name}</div>
                    <div style={{ fontSize: 12, color: '#718096' }}>{doc.title || doc.specialty}</div>
                    <div style={{ fontSize: 11, color: '#38a169', fontWeight: 600 }}>✓ Đang có lịch trống</div>
                 </div>
              </div>
            ))}
          </div>
        )}

        {msg.data?.clinics && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
            {msg.data.clinics.map(clinic => (
              <div key={clinic.clinic_id || clinic.id} className="card" style={{ cursor: 'pointer' }} onClick={() => handleSend(clinic.name)}>
                 <div style={{ fontWeight: 700, fontSize: 14, color: '#1a1a2e' }}>📍 {clinic.name}</div>
                 <div style={{ fontSize: 12, color: '#718096', marginTop: 2 }}>{clinic.address}</div>
                 <div style={{ fontSize: 11, color: '#00b5ad', fontWeight: 600, marginTop: 4 }}>Cách bạn: {clinic.dist || 'Gần nhất'}</div>
              </div>
            ))}
          </div>
        )}

        {msg.data?.slots && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginTop: 10 }}>
            {msg.data.slots.map((slot, i) => (
              <div key={i} className="card" style={{ padding: '8px 4px', textAlign: 'center', cursor: 'pointer', margin: 0 }} onClick={() => handleSend(`${slot.date} — ${slot.time}`)}>
                 <div style={{ fontWeight: 700, fontSize: 14 }}>{slot.time}</div>
                 <div style={{ fontSize: 10, color: '#718096' }}>{slot.date}</div>
                 <div style={{ fontSize: 9, color: '#38a169' }}>{slot.remaining ? `Còn ${slot.remaining} chỗ` : 'Còn chỗ'}</div>
              </div>
            ))}
          </div>
        )}

        {msg.data?.departments && (
          <div style={{ marginTop: 10 }}>
            {msg.data.departments.map(dept => (
              <button key={dept.id} className="selection-item" onClick={() => handleSend(dept.name)}>
                {dept.name}
              </button>
            ))}
          </div>
        )}

        {msg.type === 'success' && msg.data?.bookingId && (
          <div className="booking-card">
             <div className="booking-header">📋 Thông tin lịch hẹn</div>
             <div className="booking-body">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 13 }}>
                   <span style={{ color: '#718096' }}>Bệnh nhân:</span>
                   <span style={{ fontWeight: 600 }}>Nguyễn Văn A</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 13 }}>
                   <span style={{ color: '#718096' }}>Thời gian:</span>
                   <span style={{ fontWeight: 600 }}>{msg.data.time}</span>
                </div>
                <div className="booking-code">{msg.data.bookingId}</div>
                <p style={{ textAlign: 'center', fontSize: 11, color: '#718096', marginTop: 6 }}>Mã xác nhận — lưu lại để đến khám</p>
             </div>
          </div>
        )}

        {msg.options && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
            {msg.options.map(opt => (
              <button key={opt} className="selection-item" onClick={() => handleSend(opt)}>
                {opt}
              </button>
            ))}
          </div>
        )}

      </div>
    );
  };

  const initialSuggestions = [
    "Tôi bị đau bụng 3 ngày, nên khám khoa nào?",
    "Đặt lịch khám tim mạch tuần sau giúp tôi",
    "Chuẩn bị gì khi đi nội soi dạ dày?",
    "Chi phí khám tổng quát bao nhiêu?",
    "Vinmec có chấp nhận BHYT không?",
    "Tìm chi nhánh Vinmec gần Times City"
  ];

  return (
    <div className="screen-container">
      {/* Status Bar Simulator */}
      <div className="status-bar">
        <span className="time">9:41</span>
        <div style={{ display: 'flex', gap: 6 }}>
           <span>●●●●</span>
           <Clock size={12} />
           <span>95%</span>
        </div>
      </div>

      <div className="app-header">
         <div className="header-avatar">
            <svg viewBox="0 0 40 40" style={{ width: 28, height: 28 }}>
               <circle cx="20" cy="20" r="20" fill="#00b5ad"/>
               <rect x="17" y="8" width="6" height="24" rx="3" fill="white"/>
               <rect x="8" y="17" width="24" height="6" rx="3" fill="white"/>
            </svg>
         </div>
         <div className="header-info" style={{ flex: 1 }}>
            <h2>Trợ lý đặt lịch Vinmec</h2>
            <p>🟢 Đang hoạt động</p>
         </div>
         <div style={{ display: 'flex', gap: 8 }}>
            <Phone size={18} style={{ cursor: 'pointer' }} onClick={() => alert('Gọi lễ tân...')} />
            <User size={18} style={{ cursor: 'pointer' }} onClick={() => alert('Gọi bác sĩ...')} />
         </div>
      </div>

      <div className="message-list" ref={scrollRef}>
        {messages.length === 1 && messages[0].role === 'bot' && (
          <div style={{ textAlign: 'center', padding: '10px 0 20px' }}>
             <h3 style={{ fontSize: 18, fontWeight: 700, color: '#1a1a2e' }}>Bạn muốn hỏi gì hôm nay?</h3>
             <p style={{ fontSize: 13, color: '#718096', marginTop: 4 }}>Em sẵn sàng hỗ trợ anh/chị 24/7</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} style={{ display: 'flex', flexDirection: 'column' }}>
            {renderMessageContent(msg, idx === messages.length - 1)}
          </div>
        ))}

        {messages.length === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
            {initialSuggestions.map((sug, i) => (
              <div key={i} className="card" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', cursor: 'pointer', borderRadius: 16 }} onClick={() => handleSend(sug)}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#e6f6f5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#00b5ad' }}>
                  <Clock size={16} />
                </div>
                <span style={{ flex: 1, fontSize: 14, fontWeight: 500, color: '#1a1a2e' }}>{sug}</span>
                <ChevronLeft size={16} style={{ transform: 'rotate(180deg)', color: '#cbd5e0' }} />
              </div>
            ))}
          </div>
        )}

        {isTyping && (
          <div className="message bot" style={{ display: 'flex', gap: 4, width: 'fit-content' }}>
             <span className="dot"></span>
             <span className="dot"></span>
             <span className="dot"></span>
             <span style={{ fontSize: 12, color: '#a0aec0', marginLeft: 4 }}>Đang trả lời...</span>
          </div>
        )}
      </div>

      <div className="input-area">
        <input 
          type="text" 
          placeholder="Nhắn tin..." 
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={() => handleSend()}>
          <Send size={18} color="white" fill="white" />
        </button>
      </div>
    </div>
  );
};

export default App;
