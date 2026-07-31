import React from "react";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#0A0C14] py-8 text-center text-sm text-gray-505 mt-auto">
      <div className="max-w-7xl mx-auto px-4">
        <p className="text-gray-500">&copy; {new Date().getFullYear()} GoodFilms. Все права защищены.</p>
        <p className="mt-2 text-xs text-gray-600">
          Сделано с любовью для истинных любителей кино.
        </p>
      </div>
    </footer>
  );
}
