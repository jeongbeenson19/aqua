import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { getItemWithExpiry, setItemWithExpiry } from "../pages/auth";
import styles from "../styles/home.module.css";

const backendURL = process.env.REACT_APP_BACKEND_URL;

const quizTitles = {
  SCT: "스포츠 사회학",
  EDU: "스포츠 교육학",
  PSY: "스포츠 심리학",
  HIS: "한국 체육사",
  PHY: "운동 생리학",
  KIN: "운동 역학",
  ETH: "스포츠 윤리",
};

const subjectCards = [
  { id: "SCT", title: "스포츠 사회학", summary: "스포츠 문화와 사회 구조의 핵심 개념 정리" },
  { id: "EDU", title: "스포츠 교육학", summary: "지도 원리와 학습 이론 기반 실전 문제 풀이" },
  { id: "PSY", title: "스포츠 심리학", summary: "동기, 집중, 심상 훈련 영역 집중 학습" },
  { id: "HIS", title: "한국 체육사", summary: "시대별 체육사 흐름과 출제 포인트 복습" },
  { id: "PHY", title: "운동 생리학", summary: "에너지 대사와 생리 반응 이해 강화" },
  { id: "KIN", title: "운동 역학", summary: "힘, 속도, 운동 분석 문제에 대한 대응 훈련" },
  { id: "ETH", title: "스포츠 윤리", summary: "윤리 이론과 사례 중심 판단 기준 학습" },
];

function Home() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("과목");
  const [attemptedNotes, setAttemptedNotes] = useState([]);
  const [scores, setScores] = useState([]);

  const userId = getItemWithExpiry("user_id");
  const token = getItemWithExpiry("jwt_token");
  const expiryMinutes = 60;

  const attemptedNoteList = useMemo(() => {
    if (Array.isArray(attemptedNotes)) {
      return attemptedNotes;
    }

    if (attemptedNotes && typeof attemptedNotes === "object") {
      return Object.values(attemptedNotes);
    }

    return [];
  }, [attemptedNotes]);

  const averageScore = useMemo(() => {
    if (!scores.length) {
      return 0;
    }

    const total = scores.reduce((acc, item) => acc + Number(item.score || 0), 0);
    return Math.round(total / scores.length);
  }, [scores]);

  const bestSubject = scores[0] || null;

  const refreshSessionExpiry = () => {
    const storedJwtToken = localStorage.getItem("jwt_token");
    const storedUserId = localStorage.getItem("user_id");

    if (!storedJwtToken || !storedUserId) {
      return;
    }

    try {
      const parsedJwtToken = JSON.parse(storedJwtToken);
      const parsedUserId = JSON.parse(storedUserId);

      setItemWithExpiry("jwt_token", parsedJwtToken.value, expiryMinutes * 60 * 1000);
      setItemWithExpiry("user_id", parsedUserId.value, expiryMinutes * 60 * 1000);
    } catch (error) {
      console.error("세션 연장 실패:", error.message);
    }
  };

  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
    refreshSessionExpiry();
  };

  const handleSubjectClick = (quizType) => {
    if (!token) {
      alert("로그인 후 이용해 주세요.");
      navigate("/login");
      return;
    }

    refreshSessionExpiry();
    navigate(`/quiz/${quizType}`);
  };

  useEffect(() => {
    const fetchMeanScore = async () => {
      if (!userId) {
        setScores([]);
        return;
      }

      try {
        const response = await axios.get(`${backendURL}/my_page/mean_score/${userId}`);

        if (response.status === 200) {
          const meanScores = response.data.mean_scores || {};
          const updatedScores = Object.entries(meanScores)
            .filter(([key]) => Boolean(quizTitles[key]))
            .map(([key, score]) => ({
              code: key,
              subject: quizTitles[key],
              score: Math.round(Number(score) || 0),
            }))
            .sort((left, right) => right.score - left.score);

          setScores(updatedScores);
          return;
        }

        alert("마이페이지를 가져오는 데 실패했습니다.");
      } catch (error) {
        console.error("마이페이지 평균 점수 요청 실패 : ", error.message);
      }
    };

    fetchMeanScore();
  }, [userId]);

  useEffect(() => {
    const fetchAttemptedNotes = async () => {
      if (!userId || !token) {
        setAttemptedNotes([]);
        return;
      }

      try {
        const response = await axios.get(`${backendURL}/attempted/${userId}/list`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 200) {
          setAttemptedNotes(response.data.attempted_quiz_sets);
          return;
        }

        alert("오답노트를 가져오는 데 실패했습니다.");
      } catch (error) {
        console.error("오답노트 요청 실패:", error.message);
      }
    };

    fetchAttemptedNotes();
  }, [token, userId]);

  const handleExamReviewClick = (resultId, quizType, quizSetId) => {
    navigate(`/examreview/${resultId}`, {
      state: { result_id: resultId, quiz_type: quizType, quiz_set_id: quizSetId },
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("user_id");
    navigate("/login");
  };

  const getScoreLabel = (score) => {
    if (score >= 80) {
      return "상위권";
    }

    if (score >= 60) {
      return "안정권";
    }

    return "보강 필요";
  };

  return (
    <div className={styles.home}>
      <div className={styles.homeShell}>
        <header className={styles.hero}>
          <div className={styles.heroBrand}>
            <img src="/images/aqua.png" alt="aqua" className={styles.brandLogo} />
            <div>
              <p className={styles.brandCaption}>AQUA STUDY COMPANION</p>
              <h1>2급 생활스포츠지도사 학습센터</h1>
            </div>
          </div>
          <div className={styles.heroMeta}>
            <span className={styles.metaChip}>{token ? "로그인 상태" : "비로그인 상태"}</span>
            {token && (
              <button className={styles.heroActionBtn} onClick={handleLogout}>
                로그아웃
              </button>
            )}
          </div>
        </header>

        <nav className={styles.tabNav}>
          {["과목", "오답노트", "마이페이지"].map((tabName) => (
            <button
              key={tabName}
              type="button"
              className={`${styles.tabButton} ${activeTab === tabName ? styles.activeTab : ""}`.trim()}
              onClick={() => handleTabChange(tabName)}
            >
              {tabName}
            </button>
          ))}
        </nav>

        <main className={styles.mainPanel}>
          {activeTab === "과목" && (
            <section className={styles.subjectSection}>
              <div className={styles.sectionHeading}>
                <h2>오늘 학습할 과목을 선택하세요</h2>
                <p>하루 20문제로 실전 감각을 빠르게 유지할 수 있습니다.</p>
              </div>

              <div className={styles.subjectGrid}>
                {subjectCards.map((subject) => (
                  <button
                    key={subject.id}
                    type="button"
                    className={styles.subjectCard}
                    onClick={() => handleSubjectClick(subject.id)}
                  >
                    <span className={styles.subjectCode}>{subject.id}</span>
                    <h3>{subject.title}</h3>
                    <p>{subject.summary}</p>
                    <span className={styles.subjectAction}>퀴즈 시작</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          {activeTab === "오답노트" && (
            <section className={styles.noteSection}>
              <div className={styles.sectionHeading}>
                <h2>오답노트 히스토리</h2>
                <p>이전 풀이를 열어 해설과 정답 패턴을 빠르게 복습하세요.</p>
              </div>

              {attemptedNoteList.length === 0 ? (
                <div className={styles.emptyState}>
                  <h3>아직 저장된 오답노트가 없습니다.</h3>
                  <p>과목 탭에서 문제를 풀면 자동으로 기록됩니다.</p>
                </div>
              ) : (
                <ul className={styles.noteList}>
                  {attemptedNoteList.map((note, index) => (
                    <li key={note.id || `${note.quiz_set_id}-${index}`}>
                      <button
                        type="button"
                        className={styles.noteCard}
                        onClick={() =>
                          handleExamReviewClick(note.id, note.quiz_type, note.quiz_set_id)
                        }
                      >
                        <div>
                          <p className={styles.noteRound}>문제 풀이 {index + 1}회차</p>
                          <h3>{quizTitles[note.quiz_type] || "알 수 없는 과목"}</h3>
                        </div>
                        <span className={styles.noteAction}>복습하기</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {activeTab === "마이페이지" && (
            <section className={styles.analyticsSection}>
              <section className={styles.analyticsHero}>
                <div className={styles.analyticsIntro}>
                  <p className={styles.analyticsEyebrow}>Performance Snapshot</p>
                  <h2>
                    {bestSubject ? `${bestSubject.subject} 과목이 가장 안정적입니다.` : "아직 집계할 성적이 없습니다."}
                  </h2>
                  <p className={styles.analyticsDescription}>
                    마이페이지 평균은 실제로 응시한 과목만 기준으로 계산합니다. 미응시 과목은 평균과 목록에서 제외됩니다.
                  </p>
                </div>

                <div className={styles.analyticsSummary}>
                  <article className={styles.metricCard}>
                    <p>응시 과목 평균</p>
                    <h3>{scores.length ? `${averageScore}점` : "-"}</h3>
                  </article>
                  <article className={styles.metricCard}>
                    <p>응시 과목 수</p>
                    <h3>{scores.length}개</h3>
                  </article>
                  <article className={styles.metricCard}>
                    <p>누적 풀이 기록</p>
                    <h3>{attemptedNoteList.length}회</h3>
                  </article>
                </div>
              </section>

              {scores.length === 0 ? (
                <div className={styles.emptyState}>
                  <h3>아직 집계된 평균 점수가 없습니다.</h3>
                  <p>과목 탭에서 문제를 풀면 응시한 과목만 기준으로 평균이 정리됩니다.</p>
                </div>
              ) : (
                <section className={styles.scoreBoard}>
                  <div className={styles.scoreBoardHeader}>
                    <h2>과목별 평균 점수</h2>
                    <p>응시 데이터가 있는 과목만 표시합니다.</p>
                  </div>

                  <ul className={styles.scoreCardGrid}>
                    {scores.map((item, index) => {
                      const safeScore = Math.max(0, Math.min(100, item.score));

                      return (
                        <li key={`${item.code}-${index}`}>
                          <article className={styles.subjectScoreCard}>
                            <div className={styles.subjectScoreTop}>
                              <div className={styles.subjectCopy}>
                                <p className={styles.subjectRank}>#{index + 1}</p>
                                <h3>{item.subject}</h3>
                              </div>
                              <strong>{item.score}점</strong>
                            </div>

                            <div className={styles.scoreTrack}>
                              <span style={{ width: `${safeScore}%` }} />
                            </div>

                            <div className={styles.subjectMeta}>
                              <span>{item.code}</span>
                              <span>{getScoreLabel(item.score)}</span>
                            </div>
                          </article>
                        </li>
                      );
                    })}
                  </ul>
                </section>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

export default Home;
