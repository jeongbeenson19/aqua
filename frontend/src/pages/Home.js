import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getItemWithExpiry } from '../pages/auth';
import axios from 'axios';
import styles from '../styles/home.module.css';
import Plot from "react-plotly.js";
import '../styles/plot.css';

const backendURL = process.env.REACT_APP_BACKEND_URL;

function Home() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("과목");
  const [userId, setUserId] = useState(getItemWithExpiry('user_id'));
  const [token, setToken] = useState(getItemWithExpiry('jwt_token'));
  const [attemptedNotes, setAttemptedNotes] = useState([]);
  const [plotData, setPlotData] = useState();
  const [layout, setLayout] = useState(null);
  const [scores, setScores] = useState([]);

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


  // 탭 버튼 클릭 시 화면 전환
  const handleTabChange = (tabName) => {
    setActiveTab(tabName);
  };


  // 퀴즈 페이지 이동
  const handleSubjectClick = async (quizType) => {
    try {
      if (!token) {
        alert("로그인 후 이용해 주세요.");
        navigate('/login');
        return;
      }
      navigate(`/quiz/${quizType}`);
    } catch (error) {
      console.error("오류 발생:", error.message);
    }
  };


  // 마이페이지 차트
  useEffect(() => {
    const fetchPlotSunburst = async () => {
      try {
        const response = await axios.get(`${backendURL}/my_page/plot/sunburst/${userId}`, {
        });
        if (response.status === 200) {
          const parsedData = JSON.parse(response.data.plot);
          setPlotData(parsedData);
          setLayout(prevLayout => {
            const newLayout = { ...prevLayout };

            newLayout.width = 400;
            newLayout.height = 400;
            return newLayout;
          });
        }
        else {
          alert("마이페이지를 가져오는 데 실패했습니다.");
        }
      } catch (error) {
        console.error("마이페이지 차트 요청 실패 : ", error.message);
      }
    }
    fetchPlotSunburst();
  }, []);

  // 마이페이지 과목 별 평균 점수
  useEffect(() => {
    const fetchMeanScore = async () => {
      try {
        const response = await axios.get(`${backendURL}/my_page/mean_score/${userId}`);

        if (response.status === 200) {
          const { mean_scores } = response.data;

          const updatedScores = Object.keys(quizTitles).map((key) => ({
            subject: quizTitles[key],
            score: mean_scores[key] ?? 0,
          }));

          setScores(updatedScores);
        } else {
          alert("마이페이지를 가져오는 데 실패했습니다.");
        }
      } catch (error) {
        console.error("마이페이지 평균 점수 요청 실패 : ", error.message);
      }
    };

    fetchMeanScore();
  }, []);


  // 오답노트 리스트
  useEffect(() => {
    const fetchAttemptedNotes = async () => {
      try {
        const response = await axios.get(`${backendURL}/attempted/${userId}/list`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.status === 200) {
          setAttemptedNotes((response.data.attempted_quiz_sets))
        } else {
          alert("오답노트를 가져오는 데 실패했습니다.");
        }
      }
      catch (error) {
        console.error("오답노트 요청 실패:", error.message);
      }
    };
    fetchAttemptedNotes();
  }, []);

  // 오답노트 페이지 이동
  const handleExamReviewClick = async (result_id, quiz_type, quiz_set_id) => {
    try {
      navigate(`/examreview/${result_id}`, {
        state: { result_id, quiz_type, quiz_set_id }
      });
    } catch (error) {
      console.error("오류 발생:", error.message);
    }
  };


  // 로그아웃
  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_id');

    navigate('/login');
  };

  return (
    <div className={styles.home}>
      {/* 헤더 */}
      <header className={styles.header}>
        <img
          src='/images/aqua.png'
          alt="aqua"
          className={styles.aquaImage}>
        </img>
        <h1>2급 생활스포츠지도사</h1>
      </header>

      {/* 버튼 네비게이션 */}
      <nav className={styles.tab_btns}>
        <button
          className={`${styles.button} ${activeTab === "오답노트" ? styles.active : ""}`}
          onClick={() => handleTabChange("오답노트")}
        >
          오답노트
        </button>
        <button
          className={`${styles.button} ${activeTab === "과목" ? styles.active : ""}`}
          onClick={() => handleTabChange("과목")}
        >
          과목
        </button>
        <button
          className={`${styles.button} ${activeTab === "마이페이지" ? styles.active : ""}`}
          onClick={() => handleTabChange("마이페이지")}
        >
          마이페이지
        </button>

      </nav>

      {/* 탭에 따라 화면 변경 */}
      <main className={styles.tab_content}>
        {activeTab === "과목" && (
          <div className={styles.subject_ctn}>
            <button onClick={() => handleSubjectClick("SCT")}>
              스포츠 사회학
            </button>
            <button onClick={() => handleSubjectClick("EDU")}>
              스포츠 교육학
            </button>
            <button onClick={() => handleSubjectClick("PSY")}>
              스포츠 심리학
            </button>
            <button onClick={() => handleSubjectClick("HIS")}>
              한국 체육사
            </button>
            <button onClick={() => handleSubjectClick("PHY")}>
              운동 생리학
            </button>
            <button onClick={() => handleSubjectClick("KIN")}>
              운동 역학
            </button>
            <button onClick={() => handleSubjectClick("ETH")}>
              스포츠 윤리
            </button>
          </div>
        )}

        {activeTab === "마이페이지" && (
          <div className={styles.mypage_ctn}>
            {/* <div className={styles.user_info}>
              <h2 className={styles.user_name}>이름 : </h2>
              <h3 className={styles.user_email}>이메일 : </h3>
            </div> */}

            <div>
              {plotData ? (
                <Plot
                  data={plotData.data}
                  layout={layout}
                  className={styles.plot_container}
                />
              ) : (
                <p className={styles.loading_text}>
                  차트 로딩 중...
                </p>
              )}
            </div>

            <div className={styles.scores}>
              <h2 className={styles.scores_title}>과목별 평균 점수</h2>
              <ul className={styles.scores_list}>
                {scores.map((item, index) => (
                  <li key={index}>
                    <span>{item.subject} :</span>
                    <span>{item.score}점</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className={styles.actions}>
              <button className={styles.logout_btn} onClick={handleLogout}>
                로그아웃
              </button>
            </div>
          </div>
        )}
        {activeTab === "오답노트" && (
          <div className={styles.exam_history_ctn}>
            {Object.keys(attemptedNotes).length === 0 ? (
              <p className={styles.noExamMessage}>아직 시험을 풀지 않았습니다. <br />
                시험을 풀고 나면 <br />
                오답노트를 확인할 수 있습니다.
              </p>
            ) : (
              <ul className={styles.exam_history_list}>
                {Object.keys(attemptedNotes).map(key => (
                  <li key={key}>
                    <button onClick={() => handleExamReviewClick(
                      attemptedNotes[key].id,
                      attemptedNotes[key].quiz_type,
                      attemptedNotes[key].quiz_set_id
                    )}>
                      문제 풀이 {parseInt(key) + 1}회 | {quizTitles[attemptedNotes[key].quiz_type] || "알 수 없음"}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </main >
    </div >
  );
}

export default Home;
