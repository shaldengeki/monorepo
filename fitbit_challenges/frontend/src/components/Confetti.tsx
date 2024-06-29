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

type ConfettiProps = {
  colors: string[],
}

export default function Confetti({colors = ["#ffd700", "#000000"]}: ConfettiProps) {
  const refAnimationInstance = useRef(null);
  const [intervalId, setIntervalId] = useState();

  const getAnimationSettings = (angle: number, originX: number, colors: string[]) => {
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

  const nextTickAnimation = useCallback((colors: string[]) => {
    if (refAnimationInstance.current) {
      refAnimationInstance.current(getAnimationSettings(60, 0, colors));
      refAnimationInstance.current(getAnimationSettings(120, 1, colors));
    }
  }, []);

  const startAnimation = useCallback((colors: string[]) => {
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
