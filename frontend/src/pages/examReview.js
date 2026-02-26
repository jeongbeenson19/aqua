import React, { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import ReportError from "../pages/reportError";
import styles from "../styles/examReview.module.css";

function ExamReview() {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const location = useLocation();
  const locationState = location.state || {};

  const resultId = locationState.result_id || localStorage.getItem("result_id");
  const quizType = locationState.quiz_type || localStorage.getItem("quiz_type");
  const quizSetId = locationState.quiz_set_id || localStorage.getItem("quiz_set_id");

  const [quizData, setQuizData] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [isReportModalOpen, setReportModalOpen] = useState(false);

  useEffect(() => {
    if (resultId && quizType && quizSetId) {
      localStorage.setItem("result_id", resultId);
      localStorage.setItem("quiz_type", quizType);
      localStorage.setItem("quiz_set_id", quizSetId);
    }
  }, [resultId, quizSetId, quizType]);

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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = `${backendURL}/attempted/${resultId}/${quizType}/${quizSetId}`;
        const response = await axios.get(url);

        if (response.status === 200) {
          setQuizData(response.data);
          return;
        }

        throw new Error("퀴즈 데이터를 불러오는 데 실패했습니다.");
      } catch (error) {
        console.error("오류 발생:", error.message);
      }
    };

    fetchData();
  }, [backendURL, resultId, quizSetId, quizType]);

  useEffect(() => {
    if (!quizData) {
      setCorrectCount(0);
      return;
    }

    const correctAnswers = Object.values(quizData).filter((quizItem) => quizItem.is_correct).length;
    setCorrectCount(correctAnswers);
  }, [quizData]);

  const quizEntries = useMemo(() => {
    if (!quizData || typeof quizData !== "object") {
      return [];
    }

    return Object.entries(quizData);
  }, [quizData]);

  if (!quizData) {
    return (
      <div className={styles.waiting}>
        <h3>오답 노트를 불러오는 중...</h3>
      </div>
    );
  }

  const totalQuestions = quizEntries.length;
  const score = correctCount * 5;
  const accuracy = totalQuestions ? Math.round((correctCount / totalQuestions) * 100) : 0;

  return (
    <div className={styles.examReviewPage}>
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          <p>시험 복습</p>
          <h1>오답노트</h1>
        </div>

        <button
          type="button"
          className={styles.reportButton}
          onClick={() => setReportModalOpen(true)}
          aria-label="문제 오류 신고"
        >
          <img src={`${process.env.PUBLIC_URL}/images/issue.png`} alt="문제 오류 신고" />
        </button>
      </header>

      <section className={styles.summaryPanel}>
        <p className={styles.summarySubject}>{quizTitle}</p>
        <div className={styles.summaryStats}>
          <article className={styles.statCard}>
            <span>최종 점수</span>
            <strong>{score}점</strong>
          </article>
          <article className={styles.statCard}>
            <span>정답률</span>
            <strong>{accuracy}%</strong>
          </article>
          <article className={styles.statCard}>
            <span>정답 문항</span>
            <strong>
              {correctCount}/{totalQuestions}
            </strong>
          </article>
        </div>
      </section>

      <main className={styles.reviewList}>
        {quizEntries.map(([quizKey, quizItem], index) => {
          const { question_text, example, options, correct_option, description } =
            quizItem.quiz.quiz_content;
          const userAnswer = quizItem.user_answer;
          const isCorrect = Boolean(quizItem.is_correct);

          return (
            <article className={styles.reviewCard} key={`${quizKey}-${quizItem.quiz_id}`}>
              <div className={styles.reviewHead}>
                <h2>문항 {index + 1}</h2>
                <span
                  className={`${styles.reviewBadge} ${
                    isCorrect ? styles.correctBadge : styles.wrongBadge
                  }`.trim()}
                >
                  {isCorrect ? "정답" : "오답"}
                </span>
              </div>

              <p className={styles.question}>{question_text}</p>

              {Array.isArray(example) && example.length > 0 && (
                <ul className={styles.exampleList}>
                  {example.map((item, exampleIndex) => (
                    <li key={exampleIndex} className={styles.exampleItem}>
                      {item}
                    </li>
                  ))}
                </ul>
              )}

              <ul className={styles.options}>
                {Object.entries(options).map(([key, value]) => (
                  <li
                    key={key}
                    className={`${styles.option} ${
                      key === String(correct_option) ? styles.correctOption : ""
                    } ${key === String(userAnswer) ? styles.userSelected : ""} ${
                      key === String(userAnswer) && key !== String(correct_option)
                        ? styles.userWrong
                        : ""
                    }`.trim()}
                  >
                    <span>{key}</span>
                    <p>{value}</p>
                  </li>
                ))}
              </ul>

              <div className={styles.answerMeta}>
                <p>
                  <span>내가 고른 답</span>
                  <strong>{userAnswer}</strong>
                </p>
                <p>
                  <span>정답</span>
                  <strong>{correct_option}</strong>
                </p>
              </div>

              <p className={styles.description}>{description}</p>
            </article>
          );
        })}
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
