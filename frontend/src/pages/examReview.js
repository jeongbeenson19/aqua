import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import styles from '../styles/examReview.module.css';
import axios from 'axios';
import ReportError from '../pages/reportError';

function ExamReview() {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const location = useLocation();

  const locationState = location.state || {};

  const [resultId, setResultId] = useState(
    locationState.result_id || localStorage.getItem('result_id')
  );
  const [quizType, setQuizType] = useState(
    locationState.quiz_type || localStorage.getItem('quiz_type')
  );
  const [quizSetId, setQuizSetId] = useState(
    locationState.quiz_set_id || localStorage.getItem('quiz_set_id')
  );

  const [quizData, setQuizData] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);

  const [isReportModalOpen, setReportModalOpen] = useState(false);

  useEffect(() => {
    if (resultId && quizType && quizSetId) {
      localStorage.setItem('result_id', resultId);
      localStorage.setItem('quiz_type', quizType);
      localStorage.setItem('quiz_set_id', quizSetId);
    }
  }, [resultId, quizType, quizSetId]);

  // 퀴즈 과목
  const quizTitles = {
    SCT: "스포츠 사회학",
    EDU: "스포츠 교육학",
    PSY: "스포츠 심리학",
    HIS: "한국 체육사",
    PHY: "운동 생리학",
    KIN: "운동 역학",
    ETH: "스포츠 윤리",
  };

  const quizTitle = quizTitles[quizType] || "알 수 없는 퀴즈";

  // 퀴즈 데이터
  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = `${backendURL}/attempted/${resultId}/${quizType}/${quizSetId}`;
        const response = await axios.get(url);

        if (response.status === 200) {
          setQuizData(response.data);
          console.log(resultId, quizType, quizSetId);
        } else {
          throw new Error("퀴즈 데이터를 불러오는 데 실패했습니다.");
        }
      } catch (error) {
        console.error("오류 발생:", error.message);
      }
    };

    fetchData();
  }, []);

  // 점수
  useEffect(() => {
    if (quizData) {
      const correctAnswers = Object.values(quizData).filter(quizItem => quizItem.is_correct).length;
      setCorrectCount(correctAnswers);
    } else {
      setCorrectCount(0);
    }
  }, [quizData]);

  // 퀴즈 데이터가 없을 경우
  if (!quizData) {
    return <div className={styles.waiting}>
      <h3>오답 노트를 불러오는 중...</h3>
    </div>;
  }

  return (
    <div className={styles.examReview}>
      {/* 헤더 */}
      <header className={styles.header}>
        <h1>오답노트</h1>
        <img
          src="/images/issue.png"
          alt="문제 오류 신고"
          onClick={() => setReportModalOpen(true)}
        />
        <img
          src={`${process.env.PUBLIC_URL}/images/issue.png`}
          alt="문제 오류 신고"
          onClick={() => setReportModalOpen(true)}
        />
      </header>

      <main className={styles.exam_review_ctn}>
        <div className={styles.exam_review_info}>
          <h2 className={styles.exam_review_subject}>{quizTitle}</h2>
          <h3 className={styles.exam_review_score}>점수 : {correctCount * 5}</h3>
        </div>
        <div className={styles.quiz_ctn}>
          {Object.entries(quizData).map(([quizKey, quizItem], index) => {
            const { question_text, example, options, correct_option, description } = quizItem.quiz.quiz_content;
            const user_answer = quizItem.user_answer;
            return (
              <div className={styles.quiz_item} key={quizItem.quiz_id}>
                <p className={styles.question}>{index + 1}. {question_text}</p>
                {Array.isArray(example) && example.length > 0 && (
                  <ul className={styles.example_list}>
                    {example.map((item, exampleIndex) => (
                      <li key={exampleIndex} className={styles.example_item}>{item}</li>
                    ))}
                  </ul>
                )}
                <ul className={styles.options}>
                  {Object.entries(options).map(([key, value]) => (
                    <li key={key} className={`${styles.option} ${key === correct_option.toString() ? styles.correct : ''}`.trim()}>
                      {key}. {value}
                    </li>
                  ))}
                </ul>
                <p className={styles.user_answer}>내가 고른 답 : {user_answer}</p>
                <p className={styles.correct_answer}>정답 : {correct_option}</p>
                <p className={styles.description}>해설 : {description}</p>
              </div>
            );
          })}
        </div>
      </main>

      <ReportError
        isOpen={isReportModalOpen}
        onClose={() => setReportModalOpen(false)}
        quiz_type={quizType}
        quiz_set_id={quizSetId}
      />
    </div>
  );
}

export default ExamReview;