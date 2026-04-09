export const INITIAL_MESSAGES = [
  {
    role: 'bot',
    content: 'Chào bạn! Tôi là Trợ lý ảo VinmecCare. Tôi có thể giúp gì cho bạn hôm nay?',
    type: 'text'
  }
];

export const FLOW_STATES = {
  START: 'START',
  ASK_SYMPTOMS: 'ASK_SYMPTOMS',
  CLARIFYING: 'CLARIFYING',
  SAFETY_CHECK: 'SAFETY_CHECK',
  SUGGEST_DEPARTMENT: 'SUGGEST_DEPARTMENT',
  SUGGEST_DOCTOR: 'SUGGEST_DOCTOR',
  BOOKING_FORM: 'BOOKING_FORM',
  CONFIRMATION: 'CONFIRMATION'
};

export const processMessage = (message, state, history) => {
  const text = message.toLowerCase();
  
  if (state === FLOW_STATES.START) {
    return {
      reply: 'Để tư vấn tốt nhất, bạn vui lòng mô tả các triệu chứng hoặc vấn đề sức khỏe bạn đang gặp phải nhé.',
      newState: FLOW_STATES.ASK_SYMPTOMS
    };
  }

  if (state === FLOW_STATES.ASK_SYMPTOMS) {
    // Basic ambiguity check
    if (text.length < 10) {
      return {
        reply: 'Cảm ơn bạn. Bạn có thể cho tôi biết rõ hơn các triệu chứng đó bắt đầu từ khi nào và có kèm theo biểu hiện nào khác không?',
        newState: FLOW_STATES.CLARIFYING
      };
    }
    
    // Safety check for red flags
    const redFlags = ['đau ngực', 'khó thở', 'ngất', 'co giật', 'mất ý thức', 'tê'];
    if (redFlags.some(flag => text.includes(flag))) {
      return {
        reply: '⚠️ CẢNH BÁO QUAN TRỌNG: Triệu chứng bạn mô tả có thể là dấu hiệu cảnh báo đột quỵ (TIA) hoặc bệnh nghiêm trọng. Bạn nên được khám ngay trong ngày hôm nay.',
        newState: FLOW_STATES.SAFETY_CHECK,
        options: ['Gọi cấp cứu (115)', 'Tìm lịch khám khẩn cấp']
      };
    }

    return {
      reply: 'Dựa trên triệu chứng bạn mô tả, tôi gợi ý khám tại: \nKhoa Thần kinh — phù hợp với các triệu chứng đau đầu, chóng mặt. Bạn đồng ý với gợi ý này chứ?',
      newState: FLOW_STATES.SUGGEST_DEPARTMENT,
      data: {
        departments: [
          { id: 1, name: 'Đồng ý, khám Thần kinh', match: '95%' },
          { id: 2, name: 'Chọn khoa khác', match: '80%' }
        ]
      }
    };
  }

  if (state === FLOW_STATES.CLARIFYING || state === FLOW_STATES.SAFETY_CHECK || state === FLOW_STATES.SUGGEST_DEPARTMENT) {
    return {
      reply: 'Rất hiểu tình trạng của bạn. Tôi khuyên bạn nên gặp bác sĩ để có chẩn đoán chính xác nhất. Bạn muốn tôi gợi ý bác sĩ chuyên khoa hay tìm bệnh viện Vinmec gần nhất?',
      newState: FLOW_STATES.SUGGEST_DOCTOR,
      data: {
        doctors: [
          { 
            id: 1, 
            name: 'ThS. BS Lê Phan Kim Thoa', 
            specialty: 'Trưởng khoa Nhi', 
            exp: '30 năm kinh nghiệm',
            image: 'https://cdn.vinmec.com/avatars/20190507_024318_707471_BS-Thoa-2.jpg'
          },
          { 
            id: 2, 
            name: 'BSCKII Nguyễn Việt Hưng', 
            specialty: 'Nội tim mạch', 
            exp: '25 năm kinh nghiệm',
            image: 'https://cdn.vinmec.com/avatars/20190514_032517_625121_BS-Hung.jpg'
          }
        ]
      }
    };
  }

  if (state === FLOW_STATES.SUGGEST_DOCTOR) {
    return {
      reply: 'Tuyệt vời. Để đặt lịch hẹn, tôi cần một vài thông tin từ bạn. Bạn có thể xác nhận họ tên và thời gian mong muốn khám không?',
      newState: FLOW_STATES.BOOKING_FORM
    };
  }

  if (state === FLOW_STATES.BOOKING_FORM) {
    return {
      reply: 'Xác nhận thành công! Lịch hẹn của bạn đã được ghi nhận. Mã đặt chỗ: VIN-2024-8892. Thông tin chi tiết đã được gửi về số điện thoại của bạn.',
      newState: FLOW_STATES.CONFIRMATION,
      data: {
        bookingId: 'VIN-2024-8892',
        time: '09:00 - 10:00, Ngày 12/04'
      }
    };
  }

  return {
    reply: 'Tôi có thể giúp gì thêm cho bạn không?',
    newState: FLOW_STATES.START
  };
};
