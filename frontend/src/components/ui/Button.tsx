import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "glass" | "danger";
  size?: "sm" | "md" | "lg";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "primary", size = "md", children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#E8B74C] disabled:opacity-50 disabled:pointer-events-none";

    const variants = {
      primary: "bg-[#6E5CFF] hover:bg-[#5744ff] text-white shadow-lg shadow-[#6E5CFF]/20",
      secondary: "bg-white/10 hover:bg-white/20 text-white border border-white/10",
      glass: "glass-surface text-white hover:bg-white/5",
      danger: "bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-600/20",
    };

    const sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
    };

    return (
      <button
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
