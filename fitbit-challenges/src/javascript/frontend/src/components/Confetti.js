import React, { useCallback, useEffect, useRef, useState } from "react";
import ReactCanvasConfetti from "react-canvas-confetti";

const canvasStyles = {
  position: "fixed",
  pointerEvents: "none",
  width: "100%",
  height: "100%",
  top: 0,
  left: 0
};

export default function Confetti(props) {
  const {colors = ["#ffd700", "#000000"]}  = props;
  const refAnimationInstance = useRef(null);
  const [intervalId, setIntervalId] = useState();

  const getAnimationSettings = (angle, originX, colors) => {
    return {
      particleCount: 3,
      angle,
      spread: 55,
      origin: { x: originX },
      colors
    }
  }

  const getInstance = useCallback((instance) => {
    refAnimationInstance.current = instance;
  }, []);

  const nextTickAnimation = useCallback((colors) => {
    if (refAnimationInstance.current) {
      refAnimationInstance.current(getAnimationSettings(60, 0, colors));
      refAnimationInstance.current(getAnimationSettings(120, 1, colors));
    }
  }, []);

  const startAnimation = useCallback(() => {
    if (!intervalId) {
      setIntervalId(setInterval(nextTickAnimation, 16, colors));
    }
  }, [nextTickAnimation, intervalId, colors]);

  useEffect(() => {
    return () => {
      clearInterval(intervalId);
    };
  }, [intervalId]);

  startAnimation(colors);

  return (
    <>
      <ReactCanvasConfetti refConfetti={getInstance} style={canvasStyles} />
    </>
  );
}
