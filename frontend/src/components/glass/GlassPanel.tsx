import React from "react";

export const GlassPanel: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className = "", ...props }) => {
  return (
    <div className={`glass-surface rounded-2xl p-8 ${className}`} {...props}>
      {children}
    </div>
  );
};
