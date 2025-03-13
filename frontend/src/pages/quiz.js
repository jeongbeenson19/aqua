import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";
import { useParams } from "react-router-dom";
import axios from 'axios';
import ReportError from '../pages/reportError';
import { getItemWithExpiry } from '../pages/auth';
import styles from '../styles/quiz.module.css';

function Quiz() {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const [userId, setUserId] = useState(getItemWithExpiry('user_id'));
  const [token, setToken] = useState(getItemWithExpiry('jwt_token'));

  const { subjectId } = useParams();
  const navigate = useNavigate();
  const [seconds, setSeconds] = useState(0);

  const [quizData, setQuizData] = useState(null);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);

  const [isReportModalOpen, setReportModalOpen] = useState(false);

  // 퀴즈 데이터
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
          // setQuizData(response.data);
          setQuizData(response.data.quiz_set);
          console.log(response.data)

        } else {
          throw new Error("퀴즈 데이터를 불러오는 데 실패했습니다.");
        }
      } catch (error) {
        console.error("오류 발생:", error.message);
      }
    };
    fetchQuizData();

    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);

  }, []);

  // 현재 퀴즈 번호
  useEffect(() => {
    if (quizData && quizData.quiz.length > 0) {
      setCurrentQuiz(quizData.quiz[currentQuizIndex]);
    }
  }, [quizData, currentQuizIndex]);

  // mm:ss 형식으로 변환
  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  };

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

  const quizTitle = quizTitles[quizData?.quiz_type] || "알 수 없는 유형";


  // 답변 선택
  const handleAnswerSelect = (option) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[currentQuizIndex] = option;
    setUserAnswers(updatedAnswers);
  };


  // 다음 문제로 이동
  const handleNext = () => {
    console.log("userAnswers : ", userAnswers);
    console.log(userAnswers[currentQuizIndex]);
    if (userAnswers[currentQuizIndex] == null) {
      alert(`문제의 답을 선택해주세요!`);
      return;
    }

    if (currentQuizIndex < quizData.quiz.length - 1) {
      setCurrentQuizIndex((prev) => prev + 1);
    }
  };

  // 이전 문제로 이동
  const handlePrev = () => {
    if (currentQuizIndex > 0) {
      setCurrentQuizIndex((prev) => prev - 1);
    }
  };

  // 제출 버튼 클릭 시
  const handleSubmit = async () => {
    const userConfirmed = window.confirm("제출하시겠습니까?");

    if (!userConfirmed) return;

    try {
      // 결과 배열 생성
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

      // 최종 서버로 전송할 request 객체 생성
      const request = {
        quiz_set_id: quizData.quiz_set_id,
        quiz_type: quizData.quiz_type,
        score: quizResults.filter((result) => result.is_correct === 1).length * 5,
        quiz_results: quizResults,
      };

      console.log("quizResults : ", quizResults);
      console.log("request : ", request);

      alert("점수 : " + request.score);

      const API_URL = `${backendURL}/quiz/submit/${userId}`;

      const response = await axios.post(API_URL, request, {
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
    }
  }

  const question = currentQuiz?.quiz_content?.question_text || "질문을 불러오는 중입니다. 잠시만 기다려 주세요.";
  const example = currentQuiz?.quiz_content?.example || [];
  const options = currentQuiz?.quiz_content?.options || {};

  if (!quizData) {
    return <div className={styles.waiting}>
      <h2>퀴즈 데이터를 불러오는 중...</h2>
    </div>;
  }

  if (!quizData.quiz || !quizData.quiz_set_id || !quizData.type) {
    return <div className={styles.waiting}>
      <h2>존재하지 않거나 잘못된 데이터입니다.<br />
        다시 시도해주세요.</h2>
    </div>;
  }

  return (
    <div className={styles.quiz}>
      {/* 헤더 */}
      <header className={styles.header}>
        <h2 className={styles.timer}>{formatTime(seconds)}</h2>
        <h1>{quizTitle}</h1>
        <img
          src="../images/issue.png"
          alt="문제 오류 신고"
          onClick={() => setReportModalOpen(true)}
        />
      </header>

      {/* 메인 컨텐츠 */}
      <main className={styles.exam}>
        <div className={styles.exam_ctn}>
          <div className={styles.quiz_ctn}>
            <p className={styles.question}>{currentQuizIndex + 1}. {question}</p>
            {Array.isArray(example) && example.length > 0 && (
              <ul className={styles.example_list}>
                {example.map((item, index) => (
                  <li key={index} className={styles.example_item}>
                    {item}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className={styles.options_ctn}>
            {Object.entries(options)?.map(([key, option], index) => (
              <button
                key={key}
                className={
                  userAnswers[currentQuizIndex] === key
                    ? styles.selected_option
                    : styles.option
                }
                onClick={() => handleAnswerSelect(key)}
              >
                {`${key}. ${option}`}
              </button>
            ))}
          </div>
        </div>

        {/* 내비게이션 버튼 */}
        {/* <div className={styles.nav_ctn}> */}
        <div className={`${styles.nav_ctn} 
    ${currentQuizIndex === 0 || currentQuizIndex === quizData.quiz.length
            ? styles.single_button : styles.double_buttons}`}>

          {currentQuizIndex > 0 && (
            <button onClick={handlePrev} className={styles.nav_btn}>
              이전
            </button>
          )}
          {currentQuizIndex < quizData.quiz.length - 1 && (
            <button onClick={handleNext} className={styles.nav_btn}>
              다음
            </button>
          )}
          {currentQuizIndex === quizData.quiz.length - 1 && (
            <button onClick={handleSubmit} className={styles.submit_btn}>
              제출
            </button>
          )}
        </div>
      </main>

      <ReportError
        isOpen={isReportModalOpen}
        onClose={() => setReportModalOpen(false)}
        quiz_type={quizData.quiz_set_id}
        quiz_set_id={quizData.quiz_type}
      />
    </div >
  );
}

export default Quiz;