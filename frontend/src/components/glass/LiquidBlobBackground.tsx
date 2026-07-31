import React from "react";

export const LiquidBlobBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden bg-[#0A0C14]">
      {/* Blob 1: Violet */}
      <div
        className="animate-blob-1 absolute -left-[10%] -top-[10%] h-[60vw] w-[60vw] max-w-[800px] rounded-full bg-[#6E5CFF] opacity-25 blur-[120px]"
        style={{ pointerEvents: "none" }}
      />
      {/* Blob 2: Cyan */}
      <div
        className="animate-blob-2 absolute -bottom-[10%] -right-[10%] h-[60vw] w-[60vw] max-w-[800px] rounded-full bg-[#33D4C8] opacity-20 blur-[120px]"
        style={{ pointerEvents: "none" }}
      />
    </div>
  );
};
