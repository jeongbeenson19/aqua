import React from "react";
import { Routes, Route } from "react-router-dom";
import KakaoLogin from "../pages/kakaoLogin";
import Redirection from "../pages/redirection";
import Home from "../pages/Home";
import Quiz from "../pages/quiz";
import ExamReview from "../pages/examReview";
import PrivacyPolicy from "../pages/privacyPolicy";
import WeakConceptDrill from "../pages/weakConceptDrill";


const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<KakaoLogin />} />
      <Route path="/redirection" element={<Redirection />} />
      <Route path="/" element={<Home />} />
      <Route path="/quiz/:subjectId" element={<Quiz />} />
      <Route path="/drill/:subjectId" element={<WeakConceptDrill />} />
      <Route path="/examreview/:attempedId" element={<ExamReview />} />
      <Route path="/privacy-policy" element={<PrivacyPolicy />} />

    </Routes>
  );
};

export default AppRoutes;
