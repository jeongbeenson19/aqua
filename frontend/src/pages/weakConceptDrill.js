import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import { getItemWithExpiry } from "../pages/auth";
import styles from "../styles/weakConceptDrill.module.css";

function WeakConceptDrill() {
  const backendURL = process.env.REACT_APP_BACKEND_URL;
  const navigate = useNavigate();
  const { subjectId } = useParams();
  const [searchParams] = useSearchParams();

  const userId = getItemWithExpiry("user_id");
  const token = getItemWithExpiry("jwt_token");
  const topic = searchParams.get("topic") || "";
  const subTopic = searchParams.get("sub_topic") || "";

  const [seconds, setSeconds] = useState(0);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [drillData, setDrillData] = useState(null);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);

  useEffect(() => {
    if (!token || !userId) {
      navigate("/login");
      return;
    }

    if (!subjectId || !topic || !subTopic) {
      setStatus("error");
      setErrorMessage("복습할 개념 정보가 올바르지 않습니다.");
      return;
    }

    let isMounted = true;

    const fetchDrill = async () => {
      setStatus("loading");

      try {
        const response = await axios.get(`${backendURL}/users/${userId}/drill/${subjectId}`, {
          params: {
            topic,
            sub_topic: subTopic,
          },
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!isMounted) {
          return;
        }

        if (!response.data?.quiz?.length) {
          setStatus("empty");
          setErrorMessage("해당 개념으로 복습할 문제가 아직 충분하지 않습니다.");
          return;
        }

        setDrillData(response.data);
        setCurrentQuizIndex(0);
        setUserAnswers([]);
        setSeconds(0);
        setStatus("ready");
      } catch (error) {
        if (!isMounted) {
          return;
        }

        if (error.response?.status === 404) {
          setStatus("empty");
          setErrorMessage("선택한 개념에 대한 복습 문제가 없습니다.");
          return;
        }

        console.error("개념 복습 데이터를 불러오지 못했습니다:", error.message);
        setStatus("error");
        setErrorMessage("개념 복습 데이터를 불러오는 중 오류가 발생했습니다.");
      }
    };

    fetchDrill();

    return () => {
      isMounted = false;
    };
  }, [backendURL, navigate, subjectId, subTopic, token, topic, userId]);

  useEffect(() => {
    if (status !== "ready") {
      return undefined;
    }

    const timer = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [status]);

  const currentQuiz = drillData?.quiz?.[currentQuizIndex] || null;
  const totalQuestions = drillData?.quiz?.length || 0;
  const answeredCount = userAnswers.filter((answer) => answer != null).length;
  const progressPercent = totalQuestions ? ((currentQuizIndex + 1) / totalQuestions) * 100 : 0;
  const isFirstQuestion = currentQuizIndex === 0;
  const isLastQuestion = totalQuestions > 0 && currentQuizIndex === totalQuestions - 1;

  const drillResults = useMemo(() => {
    if (!drillData?.quiz?.length) {
      return [];
    }

    return drillData.quiz.map((quiz, index) => {
      const correctOption = String(quiz.quiz_content.correct_option);
      const userAnswer = userAnswers[index] == null ? "" : String(userAnswers[index]);

      return {
        quiz,
        userAnswer,
        correctOption,
        isCorrect: userAnswer === correctOption,
      };
    });
  }, [drillData, userAnswers]);

  const correctCount = useMemo(
    () => drillResults.filter((result) => result.isCorrect).length,
    [drillResults]
  );

  const accuracy = totalQuestions ? Math.round((correctCount / totalQuestions) * 100) : 0;

  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  };

  const handleAnswerSelect = (option) => {
    const updatedAnswers = [...userAnswers];
    updatedAnswers[currentQuizIndex] = option;
    setUserAnswers(updatedAnswers);
  };

  const handlePrev = () => {
    if (!isFirstQuestion) {
      setCurrentQuizIndex((prev) => prev - 1);
    }
  };

  const handleNext = () => {
    if (userAnswers[currentQuizIndex] == null) {
      alert("문제의 답을 선택해주세요!");
      return;
    }

    if (!isLastQuestion) {
      setCurrentQuizIndex((prev) => prev + 1);
    }
  };

  const handleSubmit = () => {
    if (userAnswers[currentQuizIndex] == null) {
      alert("문제의 답을 선택해주세요!");
      return;
    }

    if (userAnswers.filter((answer) => answer != null).length !== totalQuestions) {
      alert("모든 문제에 답한 뒤 제출해주세요.");
      return;
    }

    setStatus("completed");
  };

  const handleRestart = () => {
    setUserAnswers([]);
    setCurrentQuizIndex(0);
    setSeconds(0);
    setStatus("ready");
  };

  if (status === "loading") {
    return (
      <div className={styles.waiting}>
        <h2>취약 개념 복습 세트를 준비하는 중...</h2>
        <p>최근 오답과 동일 개념 문제를 우선으로 골라오고 있습니다.</p>
      </div>
    );
  }

  if (status === "empty" || status === "error") {
    return (
      <div className={styles.waiting}>
        <h2>{status === "empty" ? "복습 문제를 찾지 못했습니다." : "복습 화면을 열 수 없습니다."}</h2>
        <p>{errorMessage}</p>
        <button type="button" className={styles.primaryAction} onClick={() => navigate("/")}>
          홈으로 돌아가기
        </button>
      </div>
    );
  }

  if (status === "completed") {
    return (
      <div className={styles.page}>
        <div className={styles.shell}>
          <header className={styles.resultHero}>
            <div>
              <p className={styles.eyebrow}>RECOVERY COMPLETE</p>
              <h1>{drillData.quiz_title}</h1>
              <p className={styles.resultTopic}>
                {drillData.topic} · {drillData.sub_topic}
              </p>
            </div>

            <div className={styles.resultStats}>
              <article>
                <span>정답 수</span>
                <strong>
                  {correctCount}/{totalQuestions}
                </strong>
              </article>
              <article>
                <span>정답률</span>
                <strong>{accuracy}%</strong>
              </article>
              <article>
                <span>소요 시간</span>
                <strong>{formatTime(seconds)}</strong>
              </article>
            </div>
          </header>

          <section className={styles.summaryStrip}>
            <span>이전 오답 우선 {drillData.summary?.repeated_wrong_count || 0}문제</span>
            <span>새로운 보강 문제 {drillData.summary?.unseen_count || 0}문제</span>
            <span>총 후보 {drillData.summary?.total_candidates || totalQuestions}문제</span>
          </section>

          <div className={styles.actionRow}>
            <button type="button" className={styles.secondaryAction} onClick={handleRestart}>
              다시 복습하기
            </button>
            <button type="button" className={styles.primaryAction} onClick={() => navigate("/")}>
              홈으로 돌아가기
            </button>
          </div>

          <main className={styles.reviewList}>
            {drillResults.map((result, index) => {
              const { quiz, userAnswer, correctOption, isCorrect } = result;
              const { question_text, example, options, description } = quiz.quiz_content;

              return (
                <article className={styles.reviewCard} key={`${quiz.quiz_id}-${index}`}>
                  <div className={styles.reviewHead}>
                    <div>
                      <p className={styles.reviewIndex}>문항 {index + 1}</p>
                      <h2>{question_text}</h2>
                    </div>
                    <span
                      className={`${styles.reviewBadge} ${
                        isCorrect ? styles.correctBadge : styles.wrongBadge
                      }`.trim()}
                    >
                      {isCorrect ? "정답" : "오답"}
                    </span>
                  </div>

                  {Array.isArray(example) && example.length > 0 ? (
                    <ul className={styles.exampleList}>
                      {example.map((item, exampleIndex) => (
                        <li key={exampleIndex}>{item}</li>
                      ))}
                    </ul>
                  ) : null}

                  <ul className={styles.optionList}>
                    {Object.entries(options).map(([key, value]) => (
                      <li
                        key={key}
                        className={`${styles.optionItem} ${
                          key === correctOption ? styles.correctOption : ""
                        } ${key === userAnswer ? styles.userSelected : ""} ${
                          key === userAnswer && key !== correctOption ? styles.userWrong : ""
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
                      <strong>{userAnswer || "-"}</strong>
                    </p>
                    <p>
                      <span>정답</span>
                      <strong>{correctOption}</strong>
                    </p>
                  </div>

                  <p className={styles.description}>{description}</p>
                </article>
              );
            })}
          </main>
        </div>
      </div>
    );
  }

  const question = currentQuiz?.quiz_content?.question_text || "";
  const example = currentQuiz?.quiz_content?.example || [];
  const options = currentQuiz?.quiz_content?.options || {};

  return (
    <div className={styles.page}>
      <div className={styles.shell}>
        <header className={styles.hero}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>WEAK CONCEPT RECOVERY</p>
            <h1>{drillData.quiz_title}</h1>
            <p className={styles.heroTopic}>
              {drillData.topic} · {drillData.sub_topic}
            </p>
          </div>

          <div className={styles.heroMeta}>
            <article>
              <span>반복 오답 우선</span>
              <strong>{drillData.summary?.repeated_wrong_count || 0}문제</strong>
            </article>
            <article>
              <span>응답 완료</span>
              <strong>
                {answeredCount}/{totalQuestions}
              </strong>
            </article>
            <article>
              <span>경과 시간</span>
              <strong>{formatTime(seconds)}</strong>
            </article>
          </div>
        </header>

        <section className={styles.progressPanel}>
          <div className={styles.progressTop}>
            <strong>
              {currentQuizIndex + 1} / {totalQuestions}
            </strong>
            <span>같은 개념 문제를 연속으로 풀어 감각을 복구합니다.</span>
          </div>
          <div className={styles.progressTrack}>
            <span style={{ width: `${progressPercent}%` }} />
          </div>
        </section>

        <main className={styles.exam}>
          <article className={styles.questionCard}>
            <p className={styles.questionIndex}>문항 {currentQuizIndex + 1}</p>
            <p className={styles.question}>{question}</p>

            {Array.isArray(example) && example.length > 0 ? (
              <ul className={styles.exampleList}>
                {example.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            ) : null}
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
          <button type="button" className={styles.secondaryAction} onClick={() => navigate("/")}>
            홈으로
          </button>
          <button type="button" className={styles.secondaryAction} onClick={handlePrev} disabled={isFirstQuestion}>
            이전
          </button>
          {!isLastQuestion ? (
            <button type="button" className={styles.primaryAction} onClick={handleNext}>
              다음
            </button>
          ) : (
            <button type="button" className={styles.primaryAction} onClick={handleSubmit}>
              채점 보기
            </button>
          )}
        </footer>
      </div>
    </div>
  );
}

export default WeakConceptDrill;
