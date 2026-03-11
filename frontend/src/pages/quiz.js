import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import ReportError from "../pages/reportError";
import { getItemWithExpiry } from "../pages/auth";
import styles from "../styles/quiz.module.css";

function Quiz() {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const userId = getItemWithExpiry("user_id");
  const token = getItemWithExpiry("jwt_token");

  const { subjectId } = useParams();
  const navigate = useNavigate();

  const [seconds, setSeconds] = useState(0);
  const [quizData, setQuizData] = useState(null);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [isReportModalOpen, setReportModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchQuizData = async () => {
      try {
        const quizType = subjectId;
        const response = await axios.get(`${backendURL}/quiz/${quizType}/${userId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 200) {
          setQuizData(response.data.quiz_set);
          return;
        }

        throw new Error("퀴즈 데이터를 불러오는 데 실패했습니다.");
      } catch (error) {
        console.error("오류 발생:", error.message);
      }
    };

    fetchQuizData();

    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [backendURL, subjectId, token, userId]);

  useEffect(() => {
    if (quizData && quizData.quiz.length > 0) {
      setCurrentQuiz(quizData.quiz[currentQuizIndex]);
    }
  }, [quizData, currentQuizIndex]);

  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  };

  const quizTitles = {
    SCT: "스포츠 사회학",
    EDU: "스포츠 교육학",
    PSY: "스포츠 심리학",
    HIS: "한국 체육사",
    PHY: "운동 생리학",
    KIN: "운동 역학",
    ETH: "스포츠 윤리",
  };

  const quizTitle = quizTitles[quizData?.quiz_type] || "알 수 없는 유형";

  const handleAnswerSelect = (option) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[currentQuizIndex] = option;
    setUserAnswers(updatedAnswers);
  };

  const handleNext = () => {
    if (userAnswers[currentQuizIndex] == null) {
      alert("문제의 답을 선택해주세요!");
      return;
    }

    if (currentQuizIndex < quizData.quiz.length - 1) {
      setCurrentQuizIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuizIndex > 0) {
      setCurrentQuizIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) {
      return;
    }

    if (userAnswers[currentQuizIndex] == null) {
      alert("문제의 답을 선택해주세요!");
      return;
    }

    const userConfirmed = window.confirm("제출하시겠습니까?");

    if (!userConfirmed) {
      return;
    }

    setIsSubmitting(true);

    try {
      const quizResults = quizData.quiz.map((quiz, index) => {
        const correctOption = quiz.quiz_content.correct_option;
        const userAnswer = userAnswers[index];
        const isCorrect = Number(userAnswer) === correctOption ? 1 : 0;

        return {
          quiz_id: quiz.quiz_id,
          user_answer: userAnswer,
          is_correct: isCorrect,
        };
      });

      const request = {
        quiz_set_id: quizData.quiz_set_id,
        quiz_type: quizData.quiz_type,
        score: quizResults.filter((result) => result.is_correct === 1).length * 5,
        quiz_results: quizResults,
      };

      alert(`점수 : ${request.score}`);

      const apiUrl = `${backendURL}/quiz/submit/${userId}`;

      await axios.post(apiUrl, request, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      alert("퀴즈 제출 완료!");
      navigate(`/`);
    } catch (error) {
      console.error("퀴즈 제출 오류:", error);
      alert("퀴즈 제출 중 오류가 발생했습니다.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const question =
    currentQuiz?.quiz_content?.question_text || "질문을 불러오는 중입니다. 잠시만 기다려 주세요.";
  const example = currentQuiz?.quiz_content?.example || [];
  const options = currentQuiz?.quiz_content?.options || {};

  if (!quizData) {
    return (
      <div className={styles.waiting}>
        <h2>퀴즈 데이터를 불러오는 중...</h2>
      </div>
    );
  }

  if (!quizData.quiz || !quizData.quiz_set_id || !quizData.quiz_type) {
    return (
      <div className={styles.waiting}>
        <h2>
          내일 새로운 퀴즈가 업데이트됩니다!
          <br />
          내일 다시 도전해 보세요.
        </h2>
      </div>
    );
  }

  const totalQuestions = quizData.quiz.length;
  const progressPercent = ((currentQuizIndex + 1) / totalQuestions) * 100;
  const answeredCount = userAnswers.filter((answer) => answer != null).length;
  const isFirstQuestion = currentQuizIndex === 0;
  const isLastQuestion = currentQuizIndex === totalQuestions - 1;

  return (
    <div className={styles.quizPage}>
      <header className={styles.header}>
        <div className={styles.headerInfo}>
          <p>오늘의 과목</p>
          <h1>{quizTitle}</h1>
        </div>

        <div className={styles.headerActions}>
          <div className={styles.timer}>{formatTime(seconds)}</div>
          <button
            type="button"
            className={styles.reportButton}
            onClick={() => setReportModalOpen(true)}
            aria-label="문제 오류 신고"
          >
            <img src={`${process.env.PUBLIC_URL}/images/issue.png`} alt="문제 오류 신고" />
          </button>
        </div>
      </header>

      <section className={styles.progressPanel}>
        <div className={styles.progressTop}>
          <strong>
            {currentQuizIndex + 1} / {totalQuestions}
          </strong>
          <span>응답 완료 {answeredCount}개</span>
        </div>
        <div className={styles.progressTrack}>
          <span style={{ width: `${progressPercent}%` }} />
        </div>
      </section>

      <main className={styles.exam}>
        <article className={styles.questionCard}>
          <p className={styles.questionIndex}>문항 {currentQuizIndex + 1}</p>
          <p className={styles.question}>{question}</p>

          {Array.isArray(example) && example.length > 0 && (
            <ul className={styles.exampleList}>
              {example.map((item, index) => (
                <li key={index} className={styles.exampleItem}>
                  {item}
                </li>
              ))}
            </ul>
          )}
        </article>

        <section className={styles.optionsPanel}>
          {Object.entries(options).map(([key, option]) => (
            <button
              key={key}
              type="button"
              className={`${styles.optionCard} ${
                userAnswers[currentQuizIndex] === key ? styles.selectedOption : ""
              }`.trim()}
              onClick={() => handleAnswerSelect(key)}
            >
              <span className={styles.optionLabel}>{key}</span>
              <span className={styles.optionText}>{option}</span>
            </button>
          ))}
        </section>
      </main>

      <footer className={styles.navigation}>
        <button
          type="button"
          onClick={handlePrev}
          className={styles.navButton}
          disabled={isFirstQuestion}
        >
          이전
        </button>

        {!isLastQuestion && (
          <button type="button" onClick={handleNext} className={styles.navButton}>
            다음
          </button>
        )}

        {isLastQuestion && (
          <button type="button" onClick={handleSubmit} className={styles.submitButton} disabled={isSubmitting}>
            {isSubmitting ? "제출 중..." : "제출"}
          </button>
        )}
      </footer>

      <ReportError
        isOpen={isReportModalOpen}
        onClose={() => setReportModalOpen(false)}
        quiz_type={quizData.quiz_set_id}
        quiz_set_id={quizData.quiz_type}
      />
    </div>
  );
}

export default Quiz;
