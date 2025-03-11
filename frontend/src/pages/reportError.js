import React, { useState } from 'react';
import axios from 'axios';
import styles from '../styles/reportError.module.css';

function ReportError({ isOpen, onClose, quiz_type, quiz_set_id }) {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const [reportTitle, setReportTitle] = useState('');
  const [selectedQuizId, setSelectedQuizId] = useState(null);
  const [reportDescription, setReportDescription] = useState('');

  if (!isOpen) return null;

  const handleQuizIdChange = (e) => {
    let value = e.target.value;

    if (value < 1 || value > 20) {
      alert('1부터 20 사이의 숫자를 입력하세요!');
      return;
    }

    if (!/^\d*$/.test(value)) {
      return;
    }

    setSelectedQuizId(value);
  };

  const handleReportSubmit = async () => {
    if (!selectedQuizId || !reportTitle || !reportDescription) {
      alert("모든 항목을 올바르게 입력해주세요.");
      return;
    }

    const url = `${backendURL}/report/${quiz_type}/${quiz_set_id}/${selectedQuizId}`;

    try {
      const response = await axios.post(url, null, {
        params: {
          title: reportTitle,
          description: reportDescription
        }
      });

      if (response.status === 200) {
        alert("문제 오류 신고가 제출되었습니다.");
        onClose();
        setSelectedQuizId(null);
        setReportTitle('');
        setReportDescription('');
      } else {
        alert("신고 제출에 실패했습니다. 다시 신고해주시기 바랍니다.");
      }
    } catch (error) {
      console.error("신고 제출 중 오류 발생:", error);
      alert("네트워크 오류가 발생했습니다.");
    }
  };

  return (
    <div className={styles.modal_overlay} onClick={onClose}>
      <div className={styles.report_modal} onClick={(e) => e.stopPropagation()}>
        {/* 모달 헤더 */}
        <div className={styles.modal_header}>
          <h3>문제 오류 제출</h3>
          <button onClick={onClose}>✕</button>
        </div>

        {/* 모달 바디 */}
        <div className={styles.modal_body}>
          <label>오류 유형 선택</label>
          <select value={reportTitle} onChange={(e) => setReportTitle(e.target.value)} className={styles.select_box}>
            <option value="">선택하세요</option>
            <option value="문제 오류">문제 오류</option>
            <option value="오타 오류">오타 오류</option>
            <option value="기타 오류">기타 오류</option>
          </select>

          <label>오류 문제 번호 (1~20)</label>
          <input
            type="number"
            min="1"
            max="20"
            placeholder="번호 입력"
            value={selectedQuizId || ''}
            onChange={handleQuizIdChange}
            className={styles.input_box}
          />

          <label>문제 사항 기입</label>
          <textarea
            placeholder="오류 설명을 입력하세요"
            value={reportDescription}
            onChange={(e) => setReportDescription(e.target.value)}
            rows="4"
            className={styles.textarea_box}
          />

          <button className={styles.submit_btn} onClick={handleReportSubmit}>
            제출
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReportError;
