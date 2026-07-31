import React from "react";

export const GlassCard: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className = "", ...props }) => {
  return (
    <div className={`glass-surface rounded-xl p-6 transition-all duration-300 ${className}`} {...props}>
      {children}
    </div>
  );
};
