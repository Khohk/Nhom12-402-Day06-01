// This file acts as a bridge for the AI Agent.
// Currently it uses local logic, but you can easily swap it for a real API.

export const callAiAgent = async (message, history) => {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message, 
        history: history.map(msg => ({
          role: msg.role === 'user' ? 'user' : 'bot',
          content: msg.content
        }))
      })
    });
    
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    
    const data = await response.json();
    return {
        reply: data.response,
        newState: "CHATTING"
    };
  } catch (error) {
    console.error('API Error:', error);
    return {
        reply: "🚨 Rất tiếc, tôi đang gặp sự cố kết nối. Vui lòng thử lại sau giây lát!",
        newState: "ERROR"
    };
  }
};
