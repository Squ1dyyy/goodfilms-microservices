"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { Search, Film, User, Menu, X, ChevronDown, ChevronRight, Bookmark, Bell } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import NotificationBell from "./NotificationBell";

import { getImageUrl } from "@/components/movie/MovieCard";

/* ─────────────── Live Search ─────────────── */

function HeaderSearch({ onNavigate }: { onNavigate?: () => void }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(handler);
  }, [query]);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const { data: movies } = useQuery({
    queryKey: ["header-search-movies", debouncedQuery],
    queryFn: () => moviesQueries.getMovies({ search: debouncedQuery, limit: 5 }),
    enabled: debouncedQuery.length > 0,
  });

  const { data: persons } = useQuery({
    queryKey: ["header-search-persons", debouncedQuery],
    queryFn: () => moviesQueries.getPersons(debouncedQuery, 1, 5),
    enabled: debouncedQuery.length > 0,
  });

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && query.trim()) {
      setIsOpen(false);
      onNavigate?.();
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleSubmit = () => {
    if (query.trim()) {
      setIsOpen(false);
      onNavigate?.();
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div ref={containerRef} className="topnav-search">
      <div className="topnav-search__input-wrap">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          className="topnav-search__field"
          placeholder="Поиск фильмов и персон..."
        />
        <button
          type="button"
          className="topnav-search__btn"
          onClick={handleSubmit}
          title="Начать поиск"
        >
          <Search size={16} />
        </button>
      </div>

      {isOpen && debouncedQuery.trim() && (
        <div className="topnav-search__results">
          {movies && movies.items.length > 0 && (
            <div className="topnav-search__group">
              <h4 className="topnav-search__group-title">
                <Film size={13} /> Фильмы
              </h4>
              {movies.items.map((m) => (
                <Link
                  key={m.id}
                  href={`/movies/${m.id}`}
                  onClick={() => { setIsOpen(false); onNavigate?.(); }}
                  className="topnav-search__result-item"
                >
                  {m.poster_url && (
                    <img src={getImageUrl(m.poster_url, "w300")} alt="" className="topnav-search__thumb" />
                  )}
                  <div>
                    <span className="topnav-search__result-title">{m.title}</span>
                    <span className="topnav-search__result-year">{m.release_year}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {persons && persons.items.length > 0 && (
            <div className="topnav-search__group">
              <h4 className="topnav-search__group-title">
                <User size={13} /> Персоны
              </h4>
              {persons.items.map((p) => (
                <Link
                  key={p.id}
                  href={`/persons/${p.id}`}
                  onClick={() => { setIsOpen(false); onNavigate?.(); }}
                  className="topnav-search__result-item"
                >
                  {p.photo_url && (
                    <img src={getImageUrl(p.photo_url, "w300")} alt="" className="topnav-search__thumb topnav-search__thumb--round" />
                  )}
                  <span className="topnav-search__result-title">{p.full_name}</span>
                </Link>
              ))}
            </div>
          )}

          {(!movies || movies.items.length === 0) && (!persons || persons.items.length === 0) && (
            <div className="topnav-search__empty">Ничего не найдено</div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─────────────── Find Best Block ─────────────── */

function FindBestBlock({
  genres,
  onNavigate,
}: {
  genres: { id: number; name: string }[];
  onNavigate?: () => void;
}) {
  const router = useRouter();
  const [selectedGenre, setSelectedGenre] = useState("");
  const [selectedYear, setSelectedYear] = useState("");

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: currentYear - 1970 + 1 }, (_, i) => currentYear - i);

  const handleGo = () => {
    const params = new URLSearchParams();
    if (selectedGenre) params.set("genre_id", selectedGenre);
    if (selectedYear) params.set("year_from", selectedYear);
    if (selectedYear) params.set("year_to", selectedYear);
    onNavigate?.();
    router.push(`/movies?${params.toString()}`);
  };

  return (
    <div className="topnav-findbest">
      <span className="topnav-findbest__label">Найти лучшие фильмы</span>
      <div className="topnav-findbest__controls">
        <select
          value={selectedGenre}
          onChange={(e) => setSelectedGenre(e.target.value)}
          className="topnav-findbest__select"
        >
          <option value="">любого жанра</option>
          {genres.map((g) => (
            <option key={g.id} value={g.id}>{g.name}</option>
          ))}
        </select>
        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(e.target.value)}
          className="topnav-findbest__select"
        >
          <option value="">за всё время</option>
          {years.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        <button
          type="button"
          className="topnav-findbest__btn"
          onClick={handleGo}
        >
          Поехали!
        </button>
      </div>
    </div>
  );
}

/* ─────────────── Movies Dropdown ─────────────── */

function MoviesDropdown({ onItemClick }: { onItemClick?: () => void }) {
  const { data: genres } = useQuery({
    queryKey: ["genres"],
    queryFn: moviesQueries.getGenres,
    staleTime: 24 * 60 * 60 * 1000,
  });

  const genreList = genres || [];

  // Split genres into columns (4 columns)
  const cols = 4;
  const perCol = Math.ceil(genreList.length / cols);
  const columns: typeof genreList[] = [];
  for (let i = 0; i < cols; i++) {
    columns.push(genreList.slice(i * perCol, (i + 1) * perCol));
  }

  return (
    <div className="topnav-dropdown">
      <div className="topnav-dropdown__inner">
        <div className="topnav-dropdown__genres">
          {columns.map((col, ci) => (
            <ul key={ci} className="topnav-dropdown__genre-col">
              {col.map((genre) => (
                <li key={genre.id}>
                  <Link
                    href={`/movies?genre_id=${genre.id}`}
                    className="topnav-dropdown__genre-link"
                    onClick={onItemClick}
                  >
                    {genre.name}
                  </Link>
                </li>
              ))}
            </ul>
          ))}
        </div>
        <div className="topnav-dropdown__divider" />
        <FindBestBlock genres={genreList} onNavigate={onItemClick} />
      </div>
    </div>
  );
}

/* ─────────────── Main Header ─────────────── */

export default function Header() {
  const { accessToken } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mobileMoviesOpen, setMobileMoviesOpen] = useState(false);
  const [moviesDropdownOpen, setMoviesDropdownOpen] = useState(false);
  const dropdownCloseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Hover-intent: keep the dropdown open across small gaps (e.g. moving the
  // pointer onto the genre/year <select>s) by delaying close. Opening a native
  // <select> momentarily moves the pointer off the menu, which previously
  // collapsed a pure-CSS :hover dropdown.
  const openDropdown = useCallback(() => {
    if (dropdownCloseTimer.current) {
      clearTimeout(dropdownCloseTimer.current);
      dropdownCloseTimer.current = null;
    }
    setMoviesDropdownOpen(true);
  }, []);

  const scheduleCloseDropdown = useCallback(() => {
    if (dropdownCloseTimer.current) clearTimeout(dropdownCloseTimer.current);
    dropdownCloseTimer.current = setTimeout(() => setMoviesDropdownOpen(false), 220);
  }, []);

  const closeDropdownNow = useCallback(() => {
    if (dropdownCloseTimer.current) {
      clearTimeout(dropdownCloseTimer.current);
      dropdownCloseTimer.current = null;
    }
    setMoviesDropdownOpen(false);
  }, []);

  useEffect(() => {
    return () => {
      if (dropdownCloseTimer.current) clearTimeout(dropdownCloseTimer.current);
    };
  }, []);

  // Load genres for mobile accordion
  const { data: genres } = useQuery({
    queryKey: ["genres"],
    queryFn: moviesQueries.getGenres,
    staleTime: 24 * 60 * 60 * 1000,
  });

  const closeMobile = useCallback(() => {
    setMobileMenuOpen(false);
    setMobileMoviesOpen(false);
  }, []);

  return (
    <header className="topnav-wrapper">
      <nav className="topnav">
        {/* Logo */}
        <Link href="/" className="topnav__logo">
          <span className="topnav__logo-accent">Good</span>Films
        </Link>

        {/* Desktop Nav Items */}
        <ul className="topnav__menu">
          <li
            className={`topnav__item topnav__item--has-dropdown ${moviesDropdownOpen ? "topnav__item--open" : ""
              }`}
            onMouseEnter={openDropdown}
            onMouseLeave={scheduleCloseDropdown}
            onFocus={openDropdown}
            onBlur={(e) => {
              // Close only when focus leaves the whole item (keyboard nav).
              if (!e.currentTarget.contains(e.relatedTarget as Node)) {
                scheduleCloseDropdown();
              }
            }}
          >
            <Link
              href="/movies"
              className="topnav__item-link"
              onClick={closeDropdownNow}
            >
              Фильмы
              <ChevronDown size={14} className="topnav__item-arrow" />
            </Link>
            <MoviesDropdown onItemClick={closeDropdownNow} />
          </li>
          <li className="topnav__item">
            <Link href="/recommendations" className="topnav__item-link">
              Подбор
            </Link>
          </li>
          <li className="topnav__item">
            <Link href="/new-releases" className="topnav__item-link">
              Новинки
            </Link>
          </li>
          <li className="topnav__item">
            <Link href="/coming-soon" className="topnav__item-link">
              Скоро
            </Link>
          </li>
          <li className="topnav__item">
            <Link href="/favorites" className="topnav__item-link">
              <Bookmark size={15} />
              Закладки
            </Link>
          </li>
        </ul>

        {/* Search (Desktop) */}
        <div className="topnav__search-desktop">
          <HeaderSearch />
        </div>

        {/* Right Actions (Desktop) */}
        <div className="topnav__actions">
          <NotificationBell />
          {accessToken ? (
            <Link href="/profile" className="topnav__profile-btn">
              <User size={16} />
            </Link>
          ) : (
            <Link href="/login" className="topnav__login-link">
              Войти
            </Link>
          )}
        </div>

        {/* Mobile Toggle */}
        <div className="topnav__mobile-toggle">
          <NotificationBell />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="topnav__burger"
            aria-label="Меню"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* ─── Mobile Drawer ─── */}
      {mobileMenuOpen && (
        <div className="topnav-mobile">
          <div className="topnav-mobile__search">
            <HeaderSearch onNavigate={closeMobile} />
          </div>

          <ul className="topnav-mobile__menu">
            {/* Фильмы accordion */}
            <li>
              <button
                className="topnav-mobile__item"
                onClick={() => setMobileMoviesOpen(!mobileMoviesOpen)}
              >
                Фильмы
                <ChevronRight
                  size={16}
                  className={`topnav-mobile__chevron ${mobileMoviesOpen ? "topnav-mobile__chevron--open" : ""}`}
                />
              </button>
              {mobileMoviesOpen && (
                <div className="topnav-mobile__sub">
                  <Link
                    href="/movies"
                    onClick={closeMobile}
                    className="topnav-mobile__sub-link topnav-mobile__sub-link--all"
                  >
                    Все фильмы
                  </Link>
                  {genres?.map((g) => (
                    <Link
                      key={g.id}
                      href={`/movies?genre_id=${g.id}`}
                      onClick={closeMobile}
                      className="topnav-mobile__sub-link"
                    >
                      {g.name}
                    </Link>
                  ))}
                </div>
              )}
            </li>

            <li>
              <Link href="/recommendations" onClick={closeMobile} className="topnav-mobile__item">
                Подбор фильмов
              </Link>
            </li>
            <li>
              <Link href="/new-releases" onClick={closeMobile} className="topnav-mobile__item">
                Новинки
              </Link>
            </li>
            <li>
              <Link href="/coming-soon" onClick={closeMobile} className="topnav-mobile__item">
                Скоро в кино
              </Link>
            </li>
            <li>
              <Link href="/favorites" onClick={closeMobile} className="topnav-mobile__item">
                Закладки
              </Link>
            </li>
            <li>
              <Link href="/profile" onClick={closeMobile} className="topnav-mobile__item">
                Профиль
              </Link>
            </li>
            {!accessToken && (
              <li>
                <Link href="/login" onClick={closeMobile} className="topnav-mobile__item topnav-mobile__item--login">
                  Войти
                </Link>
              </li>
            )}
          </ul>
        </div>
      )}
    </header>
  );
}
