import React from "react";

export interface ComingSoonStateProps {
  label: string;
}

export const ComingSoonState: React.FC<ComingSoonStateProps> = ({ label }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white/5 border border-white/10 rounded-xl">
      <div className="h-12 w-12 rounded-full bg-[#E8B74C]/10 flex items-center justify-center border border-[#E8B74C]/30 text-[#E8B74C] mb-4 text-xl">
        ⏱
      </div>
      <h4 className="text-white font-semibold text-lg mb-1">{label}</h4>
      <p className="text-sm text-gray-400 max-w-sm">
        Этот раздел находится в разработке и скоро станет доступен. Следите за обновлениями!
      </p>
    </div>
  );
};
